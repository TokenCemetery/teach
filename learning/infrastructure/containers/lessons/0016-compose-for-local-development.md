---
title: "16. Compose for Local Development"
description: Describe a service and its dependencies in one Compose file, and wait for a dependency to be healthy rather than started
type: lesson
---

# Lesson 16. Compose for Local Development

**Mission link:** The mission says to run a service and its dependencies together on one host with state that survives. Compose turns the network, volume and health-check decisions of the last four lessons into one file that a teammate can start with a single command.
**Primary source:** [Docs: "Control startup and shutdown order in Compose", Docker](https://docs.docker.com/compose/how-tos/startup-order/)
**Prerequisites:** [Lesson 12](0012-health-checks-and-restart-policies.md), [Lesson 14](0014-container-networking.md), [Lesson 15](0015-volumes-and-state.md), [Compose](../GLOSSARY.md), [Health check](../GLOSSARY.md), [Named volume](../GLOSSARY.md)

## Warm-up

1. ▢ Why can one container reach another by name on a user-defined network but not on the default bridge?

<details markdown="1"><summary>Check</summary>

User-defined bridge networks use Docker's embedded DNS at `127.0.0.11`, which resolves container names and aliases. The default bridge has no name resolution, so containers on it reach each other only by IP address (lesson 14).

</details>

2. ▢ What does a health check do when it fails three times in a row, and what does it not do?

<details markdown="1"><summary>Check</summary>

It marks the container `unhealthy`, and that is all. Docker reports health and does not restart or stop on it (lesson 12). This lesson is where the report is first used: Compose can wait on it.

</details>

3. ▢ A database container is removed and recreated. Where does its data have to be for the new container to see it?

<details markdown="1"><summary>Check</summary>

In a named volume (or a bind mount) mounted at the database's data directory. The writable layer is deleted with the container (lesson 15).

</details>

## Know this

### One file, several containers

**Compose** describes a set of containers, their networks and their volumes in one YAML file, conventionally `compose.yaml`, and runs them together on one host ([Compose application model](https://docs.docker.com/compose/intro/compose-application-model/)). It is the `docker compose` command, with a space. The old standalone `docker-compose` command is the retired v1 tool. Compose does not add a new runtime: every service becomes an ordinary container, and every flag you have met has a Compose key.

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: dev-only
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  app:
    build: .
    ports:
      - "127.0.0.1:8080:8080"
    environment:
      DATABASE_URL: postgres://postgres:dev-only@db:5432/postgres
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

Read it against the earlier lessons. `image` and `build` say where the image comes from (lessons 4 and 7). `volumes` with a name uses a named volume and the top-level `volumes:` key declares it (lesson 15). `ports` is port publishing, here bound to the loopback address (lesson 14). `healthcheck` is the same check as the `HEALTHCHECK` instruction and overrides the one in the image (lesson 12). The password is a throwaway value for a local database.

### The network comes free

Compose sets up a single network for the app, using the bridge driver. Each service joins it and is reachable by other containers, and discoverable by its service name ([Networking in Compose](https://docs.docker.com/compose/how-tos/networking/)). So the app reaches the database at the hostname `db`, as in `DATABASE_URL`, and never at `localhost`, which inside the app container is the app container. A service name is a stable address across restarts, unlike an IP.

### Started is not ready

`depends_on` controls order, and its short form only waits for the dependency container to start. A started database is not one that accepts connections: it may still be initialising. The Compose docs state the problem plainly and give the answer: use `condition` with `service_healthy`, which makes Compose wait until the dependency's health check passes before creating the dependent service ([Control startup and shutdown order](https://docs.docker.com/compose/how-tos/startup-order/)). The conditions are:

|Condition|Compose waits until the dependency|
|---|---|
|`service_started`|Has started (the default of the short form)|
|`service_healthy`|Passes its health check|
|`service_completed_successfully`|Has run to completion with exit code 0, as a migration job does|

For this to work the dependency needs a `healthcheck`, which is the only place in this track where a health check changes what happens. Choose the check to mean "ready for what the dependent service needs": for a database, `pg_isready` rather than "the process exists".

An application should still retry its first connection. The condition makes the common start-up race rare, and a database can disappear later, after the order no longer matters.

### The daily commands

```console
$ docker compose up -d          # create and start everything, in the background
$ docker compose ps             # services, their state and health, and published ports
$ docker compose logs -f app    # follow one service's output
$ docker compose exec db psql -U postgres
$ docker compose up -d --build  # rebuild images, then recreate changed services
$ docker compose config         # print the file as Compose understands it
$ docker compose down           # stop and remove containers and the network
$ docker compose down -v        # also remove the volumes
```

`docker compose up --wait` starts detached and returns only when the services are running or healthy ([docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)). That is what you want in a script that goes on to use the database.

`down` removes containers and the networks Compose created, and keeps named volumes unless you add `-v`, which removes the named volumes declared in the file and anonymous volumes ([docker compose down](https://docs.docker.com/reference/cli/docker/compose/down/)). So state survives `down` and `up`, and `down -v` is the reset button that deletes it. The project name defaults to the directory name and prefixes the resource names, such as `myproject_pgdata` and `myproject_default`, which is how two copies of the same file on one host stay apart.

### Scope

Compose here is a local-development and single-host tool: one file, one machine, one command. It does not schedule across hosts, roll out updates or probe and replace containers. Those are the [Kubernetes track](../../kubernetes/README.md). A Compose file that works is a good first description of what a cluster deployment will need to express, which is the main reason to write it down.

## Practice

1. ▢ What does `depends_on: [db]` guarantee, in its short form?

    - a) That the database is ready for connections
    - b) That the database container is started first
    - c) That the database passes its health check
    - d) That the database restarts if it fails

<details markdown="1"><summary>Check</summary>

**b)** The short form orders container creation and start. (a) and (c) need `condition: service_healthy` and a health check on the dependency. (d) is a restart policy, which `depends_on` does not set.

</details>

2. ▢ Predict, then run. With the file in this lesson, what does `docker compose ps` show a few seconds after `docker compose up -d`, and in what order were the containers created?

<details markdown="1"><summary>Hint</summary>

Think about the health check's `start_period` and what `service_healthy` makes Compose do before creating `app`.

</details>

<details markdown="1"><summary>Check</summary>

`db` is created first. Compose waits for its health check to pass before creating `app`, so a few seconds after `up -d` starts, `ps` shows `db` as `Up ... (health: starting)` or `(healthy)`, and `app` may not exist yet. Once `pg_isready` passes, `app` is created. With the short `depends_on` form, both would be up at once, with `db` still initialising.

</details>

3. ▢ Predict, then run. After these commands, does the `users` table exist, and does `pgdata` exist after the last one?

    ```console
    $ docker compose up -d --wait
    $ docker compose exec db psql -U postgres -c "create table users (id int)"
    $ docker compose down
    $ docker compose up -d --wait
    $ docker compose exec db psql -U postgres -c "\dt"
    $ docker compose down -v
    $ docker volume ls
    ```

<details markdown="1"><summary>Check</summary>

The `\dt` output lists `users`: `down` removed the containers and the network but kept the named volume `pgdata`, and the new `db` container mounted it again. After `down -v`, the volume, named `<project>_pgdata`, is gone, so `docker volume ls` does not show it and the next `up` starts a fresh, empty database.

</details>

4. ▢ Add a Redis cache to the file so that `app` reaches it as `cache:6379`, publishes no port for it, and starts after it is ready.

<details markdown="1"><summary>Check</summary>

```yaml
  cache:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

and under `app`:

```yaml
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
```

The service name is the hostname, so `cache:6379` resolves on the default network. Without `ports`, Redis is reachable from the app and the host's loopback is not exposed.

</details>

5. ▢ The app logs `connection refused` to `localhost:5432` even though `db` is healthy. Name the cause and the fix.

<details markdown="1"><summary>Check</summary>

Inside the `app` container, `localhost` is the app container itself, where nothing listens on 5432. The database is a different container on the Compose network. Use the service name, `db:5432`.

</details>

6. ▢ A teammate proposes `restart: always` on every service as a substitute for `depends_on` conditions, saying the app will retry until the database is up. Give one thing it fixes, and two reasons it is not a substitute.

<details markdown="1"><summary>Check</summary>

It does fix the start-up race eventually: the app crashes, restarts after the backoff delay, and connects once the database is ready. But the restarts add delays up to a minute, fill the logs with failures that look like real incidents, and hide a missing health check. And it only covers a process that exits, so an app that blocks forever waiting for a database never restarts. Use `service_healthy` for the order and have the app retry its connection for later outages. A restart policy is for crashes, not for sequencing.

</details>

## Real-world reps

- [ ] Write a Compose file for a service you run with one dependency, add a health check to the dependency and `service_healthy` to the dependent, and bring it up with `docker compose up -d --wait`.
- [ ] Run `docker compose config` on it and read what Compose expanded. Then `docker network ls` and `docker volume ls` and find the project-prefixed names.
- [ ] Tomorrow: without notes, say what `depends_on` does by itself, what the `service_healthy` condition adds, and what the difference between `down` and `down -v` is for data.

## Going further

- [Running Containers](../reference/running-containers.md)
- [Docs: "Control startup and shutdown order in Compose", Docker](https://docs.docker.com/compose/how-tos/startup-order/)
- [Spec: Compose file reference, Docker](https://docs.docker.com/reference/compose-file/), the `services`, `depends_on` and `healthcheck` entries
- [Docs: "Networking in Compose", Docker](https://docs.docker.com/compose/how-tos/networking/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
