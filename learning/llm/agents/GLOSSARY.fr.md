---
title: "Glossaire"
description: "Termes de référence pour les agents LLM"
type: glossary
---

# Glossaire des agents LLM

Termes de référence pour construire des agents : de quoi la boucle est faite, et comment nommer chaque élément dans un domaine qui emploie couramment quatre mots pour une même chose.

## Termes

**Mémoire entre exécutions** (across-run memory) :
Faits stockés en dehors de toute trajectoire et rechargés délibérément dans le contexte initial d'une nouvelle exécution, puisqu'une nouvelle exécution démarre avec un transcript vide.
_À éviter_ : scratchpad (les deux sont des mécanismes distincts et les confondre est l'erreur la plus courante ici), état (trop générique)

**Agent** :
Système qui exécute un modèle de langage dans une boucle avec des outils, en laissant le modèle décider quel outil appeler, quand, et quand s'arrêter, au lieu de suivre un chemin que le développeur a fixé à l'avance.
_À éviter_ : assistant, bot, copilot (des mots de produit qui ne disent rien sur le caractère fixe ou décidé par le modèle du flux de contrôle)

**Boucle d'agent** :
Cycle que répète un agent en cours d'exécution : envoyer le transcript au modèle, exécuter l'appel d'outil qui revient, ajouter le résultat au transcript, recommencer jusqu'à ce qu'une condition d'arrêt se déclenche.
_À éviter_ : chaîne, pipeline (les deux désignent une séquence fixe, ce qu'une boucle d'agent n'est précisément pas)

**Point d'approbation** (approval gate) :
Point de contrôle au niveau du harness qui met la boucle en pause avant l'exécution d'un appel appartenant à une catégorie risquée, jusqu'à ce qu'un humain l'approuve ou le rejette.
_À éviter_ : human-in-the-loop (trop large ; le point d'approbation désigne ce mécanisme précis)

**Spectre d'autonomie** :
Gamme qui va d'un prompt unique à un agent dirigé par le modèle, en passant par un workflow fixé par le développeur, ordonnée selon la part du flux de contrôle que le modèle choisit à l'exécution plutôt que le développeur à l'avance.
_À éviter_ : « à quel point » quelque chose est agentique (traite l'autonomie comme une quantité floue unique au lieu d'une question de flux de contrôle dont la réponse se vérifie)

**Outil client** (client tool) :
Outil dont l'implémentation s'exécute dans le code propre du harness, si bien que le harness l'exécute directement quand le modèle le demande.
_À éviter_ : outil local, outil personnalisé

**Compaction** :
Remplacement d'un passage ancien du transcript par un résumé condensé sur lequel le modèle peut encore agir, en échangeant une partie de l'information contre un contexte résident plus petit.
_À éviter_ : résumé (trop générique ; la compaction vise précisément le transcript propre d'un agent, pas un texte quelconque)

**Confused deputy** (adjoint confus) :
Composant doté d'une autorité légitime qui est amené, par un contenu non fiable, à en abuser pour le compte d'un attaquant, sans avoir lui-même été compromis.
_À éviter_ : « le modèle a été piraté » (rien n'a été compromis : l'outil a fait exactement ce qu'il était conçu pour permettre)

**Empoisonnement du contexte** (context poisoning) :
Affirmation non étayée ou fausse qui entre dans le transcript et que chaque tour suivant traite ensuite, sans le dire, comme un fait établi.
_À éviter_ : hallucination (trop large ; ceci désigne précisément une affirmation entrée dans le transcript et qui y persiste, pas n'importe quelle sortie erronée)

**Dégradation du contexte** (context rot) :
Perte d'attention et de précision du modèle à mesure que du contenu peu pertinent s'accumule dans le contexte, même quand aucune information nécessaire n'a été tronquée.
_À éviter_ : « le contexte est plein » (confond une limite stricte de tokens avec un problème de précision plus progressif, qui commence bien avant la limite)

**Coût par tâche terminée** :
Coût en tokens de chaque tentative, nouvel essai et worker dont une tâche a réellement eu besoin pour réussir, et pas seulement le coût de l'appel final réussi.
_À éviter_ : coût par appel d'API (sous-estime une tâche qui a demandé plus d'une tentative pour réussir)

**Fan-out** :
Orchestrateur qui lance plusieurs workers en même temps sur des variantes d'un même problème, en échangeant du coût en tokens contre du temps réel en parallèle.
_À éviter_ : parallélisme (trop générique ; le fan-out est ici la forme multi-agent précise qui le produit)

**Ancrage** (grounding) :
Traduction de l'intention du modèle en une coordonnée d'écran réelle ou une cible à l'écran, étape qui peut échouer à elle seule même quand la décision sous-jacente du modèle était correcte.
_À éviter_ : précision du clic (trop étroit ; l'ancrage couvre toute correspondance entre observation et action, pas seulement le clic)

**Passation** (handoff) :
Un agent qui termine sa part d'une tâche et transmet un contexte propre et borné, pas toute sa trajectoire, à un second agent spécialisé pour la phase suivante.
_À éviter_ : fan-out (la passation est séquentielle, le fan-out est parallèle, voir le contraste dans cette leçon)

**Harness** :
Code qui entoure le modèle, conserve le transcript, exécute les appels d'outils, applique les limites et décide quand la boucle se termine. Le modèle choisit ; le harness agit.
_À éviter_ : runtime, framework (un framework est un harness possible, pas le concept)

**Moindre privilège** (least privilege) :
Limiter chaque outil à l'accès dont il a réellement besoin, plutôt qu'un accès large accordé « au cas où ».
_À éviter_ : sandboxing (un sandbox impose une frontière ; le moindre privilège est le principe de conception qui décide de l'étroitesse de cette frontière)

**Triade létale** (lethal trifecta) :
Combinaison de l'accès à des données privées, de l'exposition à du contenu non fiable et de la capacité à communiquer vers l'extérieur, qui rend ensemble un agent exploitable. Supprimer l'un des trois éléments casse l'attaque.
_À éviter_ : « risque de sécurité » (trop vague pour agir ; la triade nomme les trois conditions précises à vérifier)

**Orchestrateur** :
Agent d'un système multi-agent qui décompose une tâche, confie des sous-tâches à des workers et synthétise leurs rapports ; il ne fait pas lui-même le travail des sous-tâches.
_À éviter_ : manager, coordinateur (des termes génériques qui ne distinguent pas ce rôle de celui d'un worker)

**Injection de prompt** :
Contenu lu par un agent qui contient des instructions conçues pour détourner son comportement, en exploitant le fait que le modèle ne peut pas distinguer structurellement les données des instructions.
_À éviter_ : jailbreak (un jailbreak vise directement l'entraînement au refus du modèle ; l'injection cache des instructions dans un contenu que l'agent devait traiter)

**ReAct** :
Schéma qui entrelace une courte étape de raisonnement avec chaque action, pour que le raisonnement de chaque étape puisse réagir au résultat réel de l'étape précédente.
_À éviter_ : chain-of-thought (cela désigne le texte de raisonnement seul ; ReAct l'entrelace précisément avec des actions d'outils et leurs résultats observés)

**Réflexion** (reflection) :
Étape explicite où l'agent évalue une tentative échouée en langage naturel et reporte cette évaluation dans la tentative suivante, par opposition à un simple nouvel essai avec le même contexte.
_À éviter_ : auto-correction (employé à tort et à travers pour tout ce qu'un modèle fait en interne ; la réflexion désigne la version externe, stockée et reportée)

**Récupération à la demande** (retrieval on demand) :
Ne garder en contexte qu'un résumé ou une référence, et ne ramener le détail complet qu'au moyen d'un appel d'outil quand le modèle en a réellement besoin.
_À éviter_ : RAG (le RAG récupère dans un corpus externe ; ceci récupère du détail que l'agent a déjà produit ou auquel il a un accès direct)

**Sandbox** :
Frontière d'exécution que le harness impose autour de ce que le code d'un outil peut atteindre (système de fichiers, réseau, ressources), quoi que le modèle ait demandé.
_À éviter_ : permission (une permission est ce qu'on accorde ; un sandbox est le mécanisme qui fait respecter cet accord, même face à un appel mal formé ou hostile)

**Scratchpad** (bloc-notes) :
Notes qu'un agent écrit puis relit au sein d'une seule exécution. C'est en réalité simplement une partie du transcript, et il disparaît à la fin de l'exécution.
_À éviter_ : mémoire (un scratchpad ne survit pas à l'exécution dans laquelle il a été écrit)

**Outil serveur** (server tool) :
Outil qu'un fournisseur exécute sur sa propre infrastructure pour le compte du harness, comme une recherche web hébergée ou une exécution de code en sandbox. Le harness n'exécute jamais son implémentation, il lit seulement le résultat dans la réponse du fournisseur.
_À éviter_ : outil hébergé, outil intégré

**Sous-agent** :
Exécution d'agent distincte, avec son propre transcript et son propre harness, lancée pour accomplir un travail borné dont le seul effet sur le contexte du parent est le résumé qu'elle lui renvoie.
_À éviter_ : worker hors d'un système orchestrateur-worker (un worker est un sous-agent auquel un orchestrateur a confié une tâche bornée ; le mécanisme est le même, le terme désigne le rôle)

**Amplification de tokens** :
Combien de plus une tâche coûte en tokens sous forme de boucle agentique que sous forme de prompt unique, à cause de la recroissance du transcript, de la duplication entre agents et des nouveaux essais qui se cumulent.
_À éviter_ : « les agents coûtent cher » (trop vague ; l'amplification désigne le multiplicateur précis et l'origine de chacune de ses composantes)

**Outil** (tool) :
Capacité offerte au modèle sous la forme d'un nom, d'une description et d'un schéma de paramètres, que le modèle peut demander et que le harness exécute pour son compte.
_À éviter_ : appel de fonction (cela désigne le message que le modèle émet, pas la capacité), plugin, skill

**Trace** :
Enregistrement structuré et horodaté d'une exécution d'agent, composé de spans et fondé sur des conventions indépendantes des fournisseurs, de sorte que la trace d'un outil soit lisible dans un autre.
_À éviter_ : log (un log non structuré est ce qu'une trace remplace ; une trace a un schéma défini qu'un outil peut interroger)

**Trajectoire** :
Enregistrement complet et ordonné d'une exécution d'agent : chaque tour du modèle, appel d'outil, résultat d'outil et décision d'arrêt. C'est ce qu'on lit pour diagnostiquer un échec, plutôt que la seule réponse finale.
_À éviter_ : transcript (la liste de messages que le modèle voit réellement, qui omet les décisions propres du harness), historique, log

**Worker** :
Sous-agent auquel un orchestrateur confie une sous-tâche bornée, et qui exécute sa propre boucle et son propre transcript, isolés des autres workers.
_À éviter_ : sous-agent pour le rôle d'orchestration (le sous-agent désigne le mécanisme ; le worker désigne ce rôle précis au sein de celui-ci)

**Workflow** :
Système où un développeur a fixé à l'avance la séquence des appels au modèle et des appels d'outils. Il peut contenir des branches et des boucles, mais le modèle ne choisit pas le chemin.
_À éviter_ : agent (la distinction entre les deux est l'enjeu de l'étape 1), chaîne
