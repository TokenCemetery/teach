---
title: "15. Volumes and State"
description: Where data outlives a container in named volumes, bind mounts and tmpfs, and the file-ownership trap between host and container
type: lesson
---

# Lesson 15. Volumes and State

**Mission link:** The mission says a service and its dependencies run together on one host with state that survives. A container's writable layer dies with the container, so a database, an upload directory or a cache that matters has to live somewhere the container does not own.
**Primary source:** [Docs: "Volumes", Docker](https://docs.docker.com/engine/storage/volumes/)
**Prerequisites:** [Lesson 4](0004-images-and-layers.md), [Lesson 5](0005-from-image-to-running-container.md), [Writable layer](../GLOSSARY.md), [Named volume](../GLOSSARY.md), [Bind mount](../GLOSSARY.md), [Copy-on-write](../GLOSSARY.md)

## Warm-up

1. ▢ A container writes a file to `/data/out.txt` and is removed with `docker rm`. Where was the file, and is it still there?

<details markdown="1"><summary>Check</summary>

In the container's writable layer, the empty upper layer put over the image's layers. It is deleted with the container, so the file is gone (lesson 5).

</details>

2. ▢ What does copy-on-write do the first time a container modifies a file that came from an image layer?

<details markdown="1"><summary>Check</summary>

It copies the whole file up into the writable layer and changes the copy, so the image's read-only layers never change. This is also why heavy writes to a large file in the writable layer are slow (lesson 4).

</details>

3. ▢ A container started with `--restart always` crashes and the runtime restarts it. Is a file it wrote to its writable layer still there, and what if you run `docker rm` and `docker run` instead?

<details markdown="1"><summary>Check</summary>

After a restart the file is still there: the runtime starts the same container again, with the same writable layer (lesson 12). After `docker rm` and a new `docker run` it is gone, because that is a new container with an empty writable layer. A restart policy is not a persistence mechanism.

</details>

## Know this

### Three places data can live

Anything a container writes outside a mount goes to its writable layer, which is deleted with the container and adds the cost of copy-on-write. Data that must outlive the container goes into one of three mount types ([Volumes](https://docs.docker.com/engine/storage/volumes/)):

|Mount type|What it is|Who owns it|Typical use|
|---|---|---|---|
|Named volume|Storage Docker creates and manages under its own directory, referred to by name|Docker|A database's data directory, anything the host does not need to touch|
|Bind mount|An existing host file or directory mounted into the container|The host|Source code in development, config files, reading logs from the host|
|tmpfs|Memory-backed storage that is gone when the container stops|Nobody, it is RAM|Scratch data and secrets that must never reach disk|

Docker's own guidance is that volumes are completely managed by Docker and are a better choice than the writable layer for persistent data, and that bind mounts are the choice when you need to get at the files from both the container and the host ([Volumes](https://docs.docker.com/engine/storage/volumes/)).

### Syntax

`--mount` is explicit and `-v` is the older short form. They mean the same:

```console
$ docker volume create pgdata
$ docker run -d --name db --mount type=volume,src=pgdata,dst=/var/lib/postgresql/data postgres:17
$ docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres:17
$ docker run --rm --mount type=bind,src="$PWD"/config,dst=/etc/app,readonly alpine ls /etc/app
$ docker run --rm --tmpfs /scratch alpine df /scratch
```

A volume that does not exist when the container starts is created empty. A volume outlives the container: `docker rm db` removes the container and leaves `pgdata`. An anonymous volume, one with no name, persists too, unless the container was started with `--rm`, in which case the anonymous volume is destroyed with it. `docker volume ls`, `docker volume inspect` and `docker volume rm` manage them, and `docker volume prune` removes unused anonymous volumes only, unless you add `--all` ([docker volume prune](https://docs.docker.com/reference/cli/docker/volume/prune/)). That default protects named volumes, and `--all` is how data gets deleted.

Because a named volume is only a directory Docker manages, you back it up by mounting it into a throwaway container next to a bind mount for the output:

```console
$ docker run --rm -v pgdata:/data -v "$PWD":/backup alpine tar czf /backup/pgdata.tgz -C /data .
```

### What is already in the directory

What was at the mount point before the mount matters, and the two kinds of mount differ.

- **A bind mount hides it.** If you bind mount into a directory that has files in the image, those files are obscured by the mount, the way mounting a USB drive on `/mnt` hides what was in `/mnt`. There is no simple way to see them again short of recreating the container without the mount ([Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)).
- **An empty named volume is populated.** If you mount an empty volume over a directory that has files in the image, those files are copied into the volume by default. This is how an image ships its initial data. `volume-nocopy` turns it off. A volume that already has content is mounted as it is and hides the image's files, like a bind mount ([Volumes](https://docs.docker.com/engine/storage/volumes/)).

A bind mount source that does not exist is an error with `--mount`, and `-v` has the daemon create it as a directory, which is a classic way to get a root-owned `node_modules` or `logs` directory in a project when the daemon runs as root.

### The ownership trap

Files on a volume or bind mount have numeric owners. The kernel compares numbers, not names. A container process that runs as UID 1000 inside is UID 1000 on a rootful Linux host too, because the numbers are not mapped unless a user namespace is in use. So on Linux:

- A container running as root (UID 0) that writes to a bind mount creates root-owned files on the host. You then cannot edit or delete them without `sudo`.
- A container running as a non-root user (say UID 10001) cannot write to a bind-mounted host directory owned by UID 1000 with mode 755. The write fails with `Permission denied`.

```console
$ mkdir out
$ docker run --rm -v "$PWD/out":/out alpine touch /out/a
$ ls -ln out
-rw-r--r--  1 0 0 0 ... a
$ docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/out":/out alpine touch /out/b
$ ls -ln out
-rw-r--r--  1 1000 1000 0 ... b
-rw-r--r--  1 0 0 0 ... a
```

The fixes, from the most to the least general: run the container as the host user's IDs with `--user`; make the directory writable for the container's user, with `chown` or a group both share; or use a named volume, which Docker creates with the ownership of the image's directory, so a Dockerfile that `chown`s the mount point to the application user before the container starts fixes it for good. Rootless Docker, Podman and Docker Desktop map or hide ownership differently, so the exact symptom changes. The principle that the numbers have to match, or be mapped, does not.

## Practice

1. ▢ Which mount type fits a PostgreSQL data directory that only the database container touches?

    - a) A bind mount from the host
    - b) A named volume managed by Docker
    - c) A tmpfs mount in system memory
    - d) The container's own thin writable layer

<details markdown="1"><summary>Check</summary>

**b)** It must outlive the container, nobody on the host needs to edit it, and a volume avoids host path and ownership dependencies. (a) works but ties the data to a host path and its ownership, and the host path needs the right owner. (c) loses everything when the container stops. (d) is deleted with the container and adds copy-on-write cost to a write-heavy workload.

</details>

2. ▢ Predict, then run. What does each `cat` print?

    ```console
    $ docker run --rm -v demo:/d alpine sh -c 'echo kept > /d/f'
    $ docker run --rm -v demo:/d alpine cat /d/f
    $ docker run --rm alpine sh -c 'echo gone > /tmp/f'
    $ docker run --rm alpine cat /tmp/f
    ```

<details markdown="1"><summary>Hint</summary>

Each `docker run` starts a new container from the image. What survives from the one before?

</details>

<details markdown="1"><summary>Check</summary>

The first `cat` prints `kept`: the volume `demo` was created by the first command and mounted again by the second. The second `cat` fails with `cat: can't open '/tmp/f': No such file or directory`: the file was in the first container's writable layer, which was deleted with it, and the new container starts from the unchanged image.

</details>

3. ▢ Predict, then run. The image has `/app/data/seed.txt`. What does each `ls` show?

    ```console
    $ docker run --rm -v seeded:/app/data myimage ls /app/data
    $ mkdir empty
    $ docker run --rm -v "$PWD/empty":/app/data myimage ls /app/data
    ```

<details markdown="1"><summary>Hint</summary>

One mount type copies the image's files into an empty target and the other hides them.

</details>

<details markdown="1"><summary>Check</summary>

The first shows `seed.txt`: `seeded` does not exist, so it is created empty, and an empty named volume mounted over a directory with files gets those files copied in. The second shows nothing: the bind mount hides the image's directory with the host's empty one. Run the first again after deleting `seed.txt` from the volume and it stays deleted, because the volume now has content and is no longer populated.

</details>

4. ▢ Predict, then run. On a rootful Linux host, who owns `out/a` and `out/b` and can you delete them as yourself?

    ```console
    $ mkdir out
    $ docker run --rm -v "$PWD/out":/out alpine touch /out/a
    $ docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/out":/out alpine touch /out/b
    $ ls -ln out
    ```

<details markdown="1"><summary>Check</summary>

`a` is owned by UID 0 and GID 0, `b` by your own UID and GID. You can delete `b`, and you can delete `a` only because the directory `out` is yours, since removing a file needs write access to its directory and not to the file. You cannot edit `a` without `sudo`, and the second command only worked because you own `out`. With `out` owned by root and mode 755, the second command fails with `Permission denied`.

</details>

5. ▢ A service runs as UID 10001 in its image and writes uploads to `/var/uploads`. You mount a named volume at `/var/uploads` and it fails with `Permission denied` on the first write. The Dockerfile never created the directory. What is wrong, and what is the fix?

<details markdown="1"><summary>Check</summary>

The mount point did not exist in the image, so Docker created `/var/uploads` as root-owned, and an empty volume takes the ownership of the image's directory at that path. The non-root user cannot write to it. Create the directory in the Dockerfile and give it to the application user before the volume is first mounted: `RUN mkdir -p /var/uploads && chown 10001:10001 /var/uploads`, with the `USER` instruction after it. The same shape of fix does not work for a bind mount, whose ownership comes from the host.

</details>

6. ▢ A teammate runs `docker volume prune --all` "to clear space" on the shared build host. What does it delete, and how would you have recovered the database volume that was in it?

<details markdown="1"><summary>Check</summary>

All volumes not referenced by any container, named ones included. A stopped database container still references its volume, so that one is safe. A volume whose container was removed is not, and it is gone with no trash to recover it from. The recovery is a backup made earlier, for example the `tar` through a throwaway container above, which is why the backup comes before the cleanup. Plain `docker volume prune` removes only unused anonymous volumes.

</details>

## Real-world reps

- [ ] Start a container with a named volume, write a file, remove the container, start a new one on the same volume and read the file back. Then run `docker volume inspect` and find where Docker stores it.
- [ ] Back up one of your own volumes with the `tar` command in this lesson and list the archive.
- [ ] Tomorrow: without notes, name the three mount types, say what a bind mount does to files already in the target directory, and say what the ownership of a file written by a root container looks like on a Linux host.

## Going further

- [Running Containers](../reference/running-containers.md)
- [Docs: "Volumes", Docker](https://docs.docker.com/engine/storage/volumes/)
- [Docs: "Bind mounts", Docker](https://docs.docker.com/engine/storage/bind-mounts/)
- [Docs: "docker volume prune", Docker CLI reference](https://docs.docker.com/reference/cli/docker/volume/prune/), for what prune removes by default
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
