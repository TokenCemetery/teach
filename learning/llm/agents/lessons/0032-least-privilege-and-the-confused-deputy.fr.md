---
title: "32. Moindre privilège et confused deputy"
description: "Comment limiter les capacités d'un agent pour qu'une injection de prompt cause des dégâts contenus plutôt qu'une brèche catastrophique"
type: lesson
---

# Leçon 32. Moindre privilège et confused deputy

**Lien avec la mission :** Concevoir les frontières d'accès de chaque outil d'agent pour que du contenu non fiable puisse tromper l'agent mais ne puisse pas le tromper au point de lui faire abuser de capacités qu'il n'aurait jamais dû avoir.
**Source primaire :** [Référence : "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
**Prérequis :** [Leçon 31](0031-prompt-injection-and-the-lethal-trifecta.md), [Sandbox](../GLOSSARY.md)

## Échauffement

1. ▢ Nommez les trois conditions de la triade létale de la leçon 31.

<details markdown="1"><summary>Vérifier</summary>

L'accès à des données privées, l'exposition à du contenu non fiable et la capacité à communiquer vers l'extérieur. Supprimez-en une et l'attaque échoue.

</details>

2. ▢ Dans la leçon 31, vous avez conçu un outil pour éviter une attaque par injection de prompt en brisant une condition de la triade. Si vous aviez brisé la condition de communication externe, décrivez à quoi cela ressemblerait en pratique.

<details markdown="1"><summary>Vérifier</summary>

L'outil ne pourrait soit rien envoyer nulle part, soit n'envoyer que vers un canal que l'attaquant ne peut pas atteindre. Par exemple, un outil draft_email qui ne fait que stocker les e-mails localement au lieu de les envoyer, ou un outil qui ne peut écrire que dans une table d'attente exigeant une relecture manuelle avant que les données ne soient partagées.

</details>

## À savoir

### Moindre privilège : limiter chaque outil à exactement ce dont il a besoin

Le moindre privilège est un principe de sécurité : chaque outil ne devrait avoir accès qu'à la ressource ou à l'action précise dont il a réellement besoin, et pas à un accès large « au cas où cela servirait plus tard ». Pour un agent, cela signifie concevoir la frontière de sandbox de chaque outil avec une permission étroite.

Exemples :

- Un outil qui lit l'agenda du jour ne devrait lire que le fichier de calendrier, pas tout le système de fichiers
- Un outil qui consulte la commande d'un client ne devrait interroger que les commandes de ce client, pas toutes les commandes de l'entreprise
- Un outil qui envoie un e-mail de reçu ne devrait pouvoir envoyer que depuis une adresse fixe, pas depuis toute la boîte aux lettres
- Un outil qui modifie un fichier de configuration ne devrait modifier que ce fichier, pas des fichiers arbitraires du répertoire de configuration

Le principe s'applique aussi aux identifiants. Si un outil doit s'authentifier auprès d'un service externe, il devrait utiliser un identifiant limité à ce service et à cette action, pas un compte administrateur large.

Pourquoi cela compte-t-il pour les agents ? Parce qu'un accès large est exactement ce qui rend une exploitation coûteuse pour l'organisation. Quand un agent est trompé par une injection pour appeler un outil auquel il a accès, les conséquences dépendent de ce que cet outil peut réellement atteindre.

### Le schéma du confused deputy : une autorité légitime, détournée

Le confused deputy (adjoint confus) est un schéma de sécurité classique, nommé pour la première fois dans les années 1980, qui s'applique directement aux agents. Un confused deputy est un programme doté d'une autorité légitime et large qui est amené à en abuser pour le compte d'un attaquant. Le programme n'est pas compromis au sens où il exécuterait du code malveillant ; il fait exactement ce que ses outils légitimes permettent, simplement pour le compte d'instructions qui n'ont jamais été celles de l'utilisateur.

Un agent atteint d'une vulnérabilité de confused deputy ressemble à ceci :

1. L'agent a un outil large : send_email peut envoyer depuis n'importe quelle adresse de la boîte aux lettres de l'entreprise
2. L'agent lit du contenu non fiable : une invitation de calendrier avec une instruction injectée
3. L'instruction demande à l'agent de transférer un fil d'e-mails confidentiel à une adresse externe
4. L'agent appelle send_email avec les paramètres de l'attaquant
5. L'outil exécute l'appel parce que c'est un appel send_email légitime avec des paramètres valides. L'outil ne sait pas que la demande provient d'une injection et non de l'intention réelle de l'utilisateur.

L'e-mail est maintenant exfiltré, non pas parce que le modèle a été « piraté », mais parce que vous avez donné à un agent une capacité large et ne l'avez pas limitée à une tâche étroite.

La correction n'est pas de prompter le modèle plus fort. La correction est de concevoir l'outil de façon étroite : au lieu de send_email pour toute la boîte aux lettres, concevoir un outil appelé send_receipt qui ne peut envoyer qu'à des adresses e-mail de clients avec un gabarit fixe. Maintenant, une injection peut encore tromper le modèle pour qu'il appelle send_receipt, mais cet appel est contraint à ce que send_receipt a le droit de faire.

### Chaîne d'approvisionnement MCP : la confiance est transitive

Les leçons 20 et 21 ont couvert le Model Context Protocol (MCP) et la façon dont un agent se connecte à des serveurs MCP pour accéder à des outils. Sous l'angle de la sécurité, se connecter à un serveur MCP signifie étendre votre frontière de confiance à quiconque exploite ce serveur.

Un serveur MCP malveillant ou compromis peut :

- Dénaturer les descriptions d'outils pour faire passer des appels nuisibles pour bénins
- Renvoyer des données trompeuses dans les résultats d'outils, sur lesquelles l'agent raisonnera ensuite
- Observer chaque appel d'outil de l'agent et chaque élément de contexte qu'il envoie

Quand votre harness se connecte à un serveur MCP tiers, vous faites confiance à l'opérateur de ce serveur autant qu'à votre propre code. Si le serveur est compromis ou exploité par un adversaire, il devient un canal d'injection supplémentaire.

La défense est la même que pour tout risque de chaîne d'approvisionnement : ne se connecter qu'à des serveurs de confiance, et limiter la connexion. Par exemple :

- Ne pas donner à un agent l'accès à tous les serveurs MCP disponibles ; ne se connecter qu'aux serveurs précis dont il a besoin
- Utiliser l'authentification et le chiffrement pour les connexions MCP
- Auditer les descriptions d'outils qu'un serveur MCP fournit et comprendre quel accès vous accordez
- Partir du principe que les données que vous envoyez à un outil MCP pourraient devenir publiques ou être détournées

Les serveurs MCP ne sont pas particulièrement risqués ; ils ne sont qu'un outil de plus. Le principe est le même : limiter l'accès.

### En résumé : des frontières de permissions par outil et par tâche

Le principe de conception qui relie ces leçons est qu'une frontière de permissions doit être délimitée délibérément, par outil et par tâche, plutôt que par un identifiant large unique que tout l'agent partage.

Quand vous concevez un agent :

1. Listez chaque outil dont l'agent a besoin
2. Pour chaque outil, demandez-vous : quel est l'accès minimal dont cet outil a besoin pour remplir sa fonction ?
3. Créez une frontière de sandbox pour cet outil qui accorde exactement cet accès, pas plus
4. Si un outil doit s'authentifier (auprès d'une base de données, d'une API, d'un système de fichiers), créez un identifiant limité à cet outil et à ce niveau d'accès, pas un identifiant qui peut tout atteindre

Un outil étroitement délimité est la chose concrète qui transforme « le modèle a été trompé par une injection » d'un compromis catastrophique en une erreur contenue, à faible conséquence. L'agent lit l'injection, le modèle la comprend, le modèle appelle l'outil visé par l'injection, et l'outil refuse d'exécuter l'action demandée parce que l'action sort de son périmètre.

## Pratique

1. ▢ Vous concevez un outil pour un agent qui gère des comptes utilisateurs. L'outil doit mettre à jour l'adresse e-mail d'un utilisateur dans la base de données de l'entreprise. Votre premier brouillon lui donne cet identifiant : un compte de base de données avec la permission UPDATE sur toute la table users.

Pourquoi est-ce trop large, et quelle serait une meilleure conception ?

<details markdown="1"><summary>Vérifier</summary>

L'identifiant accorde la permission UPDATE sur toute la table, ce qui signifie que l'outil pourrait mettre à jour les informations de n'importe quel utilisateur, pas seulement l'adresse e-mail précise de l'utilisateur précis dont on s'occupe. Une meilleure conception créerait une procédure stockée dans la base de données qui n'accepte que l'identifiant de l'utilisateur et le nouvel e-mail, et accorderait à l'identifiant de l'outil la permission d'exécuter seulement cette procédure. Ainsi, même si une injection trompe l'agent pour qu'il appelle l'outil avec des paramètres inattendus, la base de données refusera d'exécuter quoi que ce soit hors du périmètre de la procédure.

</details>

2. ▢ Un agent a accès à un outil send_email limité à l'envoi depuis `support@company.com` uniquement et vers des adresses e-mail correspondant au motif `*@customer-*.com` uniquement. Une injection tente de le tromper pour envoyer un message à `attacker@evil.com`. Qu'est-ce qui arrête l'attaque ?

<details markdown="1"><summary>Indice</summary>

C'est l'outil lui-même qui impose le périmètre. Pensez à l'endroit où cette vérification a lieu et à la raison pour laquelle aucune instruction de prompt n'est en jeu.

</details>

<details markdown="1"><summary>Vérifier</summary>

La validation de l'outil, qui s'exécute dans le harness avant l'envoi du message. L'outil valide le destinataire par rapport à son motif autorisé et refuse d'envoyer parce que `attacker@evil.com` ne correspond pas. L'injection a réussi à changer le comportement de l'agent (l'agent avait l'intention d'envoyer), mais elle a échoué parce que la frontière de permissions de l'outil a empêché l'action nuisible. C'est un contrôle au niveau de l'outil, pas au niveau du prompting, donc il est fiable.

</details>

3. ▢ Votre organisation fournit un serveur MCP qui expose des événements du calendrier de l'entreprise. Vous découvrez qu'une entreprise tierce a construit un client MCP qui se connecte à votre serveur pour aider à gérer des réunions. Lequel de ces énoncés est vrai ?

    - a) C'est sans danger tant que votre serveur MCP ne renvoie que des données de calendrier publiques
    - b) Le client tiers a désormais de fait un accès en lecture aux données de calendrier que votre serveur renvoie
    - c) Vous devriez utiliser le chiffrement entre votre serveur et le client pour garantir que même les opérateurs de votre serveur ne peuvent pas voir les données
    - d) L'entreprise tierce ne peut pas détourner les données parce qu'il ne s'agit que d'événements de calendrier, pas d'identifiants d'utilisateurs

<details markdown="1"><summary>Vérifier</summary>

**b)** Le client tiers, et quiconque l'exploite, peut voir et potentiellement détourner toutes les données de calendrier que le serveur renvoie. Une donnée publique reste une donnée ; même si les événements du calendrier ne sont pas secrets, l'opérateur tiers a maintenant de la visibilité sur l'emploi du temps de votre organisation, ce qui pourrait servir à l'espionnage industriel ou à l'ingénierie sociale. Le chiffrement (option c) protégerait les données en transit, mais n'empêcherait pas l'opérateur du client de les voir. L'étendue de l'accès (public contre privé) ne change pas l'implication de sécurité : vous avez étendu votre frontière de confiance à l'opérateur tiers. C'est le risque de chaîne d'approvisionnement MCP.

</details>

4. ▢ Vous concevez un outil pour un agent qui traite des tickets de support client. L'outil doit envoyer une réponse par e-mail à un client. Décrivez une conception de moindre privilège qui empêcherait une attaque de confused deputy où une injection tromperait l'agent pour qu'il transfère un fil d'e-mails interne confidentiel à un client.

<details markdown="1"><summary>Vérifier</summary>

Au lieu d'un outil générique send_email, concevoir un outil appelé send_support_response qui ne prend que deux paramètres : l'identifiant du ticket et le texte de la réponse. L'outil cherche l'adresse e-mail du client à partir de l'identifiant du ticket, valide que le texte de la réponse ne dépasse pas une longueur raisonnable, et n'envoie que la réponse (pas de pièces jointes, pas d'autres e-mails). L'identifiant de l'outil n'a la permission d'envoyer que depuis l'adresse du support et que vers des adresses e-mail de clients liées à des tickets valides. Maintenant, une injection peut tromper l'agent pour qu'il appelle send_support_response, mais l'appel est contraint par le périmètre de l'outil. L'agent ne peut pas transférer d'e-mails internes, ne peut pas envoyer à des adresses arbitraires, et ne peut rien envoyer qui ne soit une réponse de support parce que l'outil n'offre aucun moyen de faire ces choses.

</details>

## Exercices en situation réelle

- [ ] Prenez un outil que vous avez conçu ou que vous utilisez fréquemment. Relevez ses permissions actuelles. Notez une permission qu'il a et qui dépasse ce dont il a strictement besoin pour son but principal, et une façon de la retirer.
- [ ] Choisissez un serveur MCP auquel vous accepteriez de connecter un agent. Renseignez-vous ou contactez l'opérateur pour comprendre : quelles données le serveur voit-il, comment sont-elles utilisées, comment sont-elles protégées, qui a accès aux logs ? Notez votre niveau de confiance et tout risque résiduel.
- [ ] Demain : concevez un outil qui met en œuvre délibérément le moindre privilège en refusant une demande plausible mais hors périmètre. Écrivez une spécification qui nomme la demande qu'il recevrait lors d'une attaque de confused deputy et explique pourquoi la conception de l'outil l'empêche de réussir.

## Pour aller plus loin

- [Référence : "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
