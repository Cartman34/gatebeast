# Les artefacts publiés — les règles du registre

**Usage :** ce qu'il faut savoir avant de publier quoi que ce soit, et comment se tient le registre. **Les données, elles, vivent dans `review-server/artefacts.json`** — un artefact, son état, son
adresse — et **ce document n'en recopie aucune**. C'est de ce fichier que l'index se construit ; l'ouvrir est le geste qui précède toute publication, puis on liste les artefacts existants pour
vérifier qu'il n'en manque aucun : le registre peut être en retard, la liste réelle fait foi. On republie sur une adresse existante, on n'en crée jamais une neuve pour un sujet qui en a déjà une.

**Pourquoi la donnée n'est pas ici** (opérateur, 2026-08-07) : elle vivait dans un tableau de `SUIVI.md`, et l'index allait l'y lire. Le suivi est le document de travail de l'agent — il se réécrit
sans cesse, et **il n'a pas à servir de source de données à l'application**. Une donnée vit à un seul endroit : celui d'où l'outil la lit.

**Le format est du JSON, et ce n'est pas un choix de goût** : PHP n'embarque pas de lecteur YAML, et en ajouter un est une dépendance à installer sur toute machine où le projet tourne — donc une
décision de l'opérateur. Le JSON est natif, et c'est déjà le format du référentiel des sujets. **Le YAML se ferait volontiers** si l'opérateur veut l'extension.

**Intention :** une adresse non consignée est une adresse perdue, et le suivant en crée une de plus. C'est arrivé le 2026-08-06 : la maquette du parc a reçu une seconde adresse, et **les remarques que
l'opérateur y avait posées ont été perdues** — elles vivent dans le navigateur, attachées à la page qui les a reçues. Ce registre est un document à part, et non une section du suivi : le suivi dit où
en est le travail et se réécrit sans cesse, tandis qu'une adresse est durable et doit se trouver du premier coup.

**Un artefact, un sujet, plusieurs supports possibles.** Le même artefact peut être servi à plusieurs endroits — une page Claude aujourd'hui, une adresse chez le générateur ou un hébergement propre
demain. Chaque support porte son **identifiant** quand il en a un, parce que c'est lui qui permet de republier au bon endroit ; l'adresse complète, elle, se lit et se colle.

**Depuis le 2026-08-07, le support de travail est le serveur local.** Les pages de revue qu'on utilise vivent sous `review-server/` et une commande les sert toutes (`php review-server/serve.php`).
**L'adresse n'est pas écrite ici : elle est configurée dans `review-server/config.json`, et `php review-server/url.php` la dit** — le port se change là, une fois, et tout le suit. Les artefacts
Claude ne disparaissent pas pour autant : ils restent inscrits ici, leurs adresses restent valables, et il pourra y en avoir d'autres. Ce
registre continue donc de faire foi pour ce qui est **publié** — ce qui est servi en local n'a pas d'adresse à tenir, c'est tout l'intérêt.

**Quatre états, et seuls ces quatre-là.** **Vivant** : on s'en sert, il se republie. **Archivé** : plus actif, mais consultable, et son adresse reste valable — archiver n'est pas supprimer. **Clos** :
son sujet est tranché, il ne bougera plus. **À ne pas rouvrir** : un doublon créé par erreur, sur lequel on ne republie jamais ; il reste inscrit jusqu'à ce que l'opérateur le supprime, et sa ligne
disparaît alors avec lui.

**CE QUI EST ARCHIVÉ N'EST PLUS MAINTENU** (opérateur, 2026-08-07), et c'est le sens même du mot ici : on ne le reconstruit pas, on ne le corrige pas, on ne le suit pas. **Il prendra donc de la
dette** — le jour où on le restaure, il aura pris du retard sur tout ce qui a bougé entre-temps. Cette dette est **acceptée d'avance et connue**, puisque la règle la dit : elle n'a pas à être
signalée à chaque fois, ni à être rattrapée en douce au passage. Ce qui vaut pour une page publiée vaut pour tout ce que le projet archive, page servie comprise.

## Archiver, geste par geste

**Intention :** l'essentiel de l'archivage, c'est **qu'il se voie** — la chose quitte les vivants de l'index et se retrouve sous « Archivés ». Un archivage qui ne change que le code laisse tout le
monde croire que la page est encore tenue. Constaté le 2026-08-07 : les deux pages du parc ont été retirées du serveur et décrites comme archivées, **sans que l'index bouge d'un pixel**, parce que
l'état vivait à deux endroits et que je n'en avais changé qu'un. Il n'en a plus qu'un depuis, et c'est ce qui empêche l'oubli de se reproduire.

**Les deux gestes, et aucun n'est facultatif :**

1. **Le passer à l'état `archived` dans `review-server/artefacts.json`.** C'est ce geste-là, et lui seul, qui le fait descendre sous « Archivés » dans l'index.
2. **Le retirer des pages servies** — son entrée sort de la déclaration des pages du serveur de revue, gardée en commentaire juste à côté pour que la restauration soit une ligne à remettre. Son
   constructeur et sa page restent sur le disque : archiver n'est pas supprimer.

## Où se lit la liste

**Nulle part ici.** La liste — nom, description, état, adresse, ce qui produit chaque artefact — vit dans `review-server/artefacts.json`, et **la recopier ici serait exactement la faute que ce
document vient de corriger** : deux listes divergent toujours, et c'est celle que personne ne lit qui reste juste.

**Pour la voir, on ouvre l'index** : `php review-server/serve.php`, puis l'adresse qu'il imprime. Il montre les quatre états, chacun dans sa section, chaque artefact avec son adresse. C'est la même
liste que le fichier, rendue lisible — et c'est la seule façon de la consulter sans ouvrir de fichier, comme le veut la règle qui demande qu'une donnée sortie de la documentation reste consultable.

**Une entrée mal formée ne fait pas taire l'index** : elle est écartée et signalée en bas de page, avec ce qui cloche. Un état inconnu, un nom manquant, une adresse qui n'en est pas une : chacun se
dit. Ce qui ne se voit pas, c'est une entrée juste mais fausse — d'où le geste qui précède toute publication, lister les artefacts existants et confronter.
