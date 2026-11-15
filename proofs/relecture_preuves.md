# Relecture des preuves écrites (`preuves.md`) — problème 3, session 3

Relecteur indépendant. Je n'ai écrit ni le code ni les preuves. Date : 2026-11-14, de 07:34:52 à 07:46:26, soit environ 12 min (horodatages du journal de session, non distribué), donc bien moins que l'heure prévue. Pour la durée, je n'ai pas de journal plus fin que ces deux horodatages.

*Document historique.* Les sections et verdicts ci-dessous sont ceux de la session 3. Le 15 novembre 2026 (session 4), les renvois aux fichiers de travail ont été remplacés par les fichiers et fonctions du dépôt distribué (commit `3af8dfe`), et les chemins locaux ont été retirés. Rien d'autre n'a été changé dans les sections 1 à 5 ; voir la section finale « Mise à jour du 15 novembre 2026 (session 4) ».

## Table de correspondance « ancien fichier/fonction → fichier/fonction actuels »

La relecture a porté sur les fichiers de travail des sessions 2 et 3. Leur contenu se retrouve, renommé et traduit, dans le dépôt distribué. Les anciens noms ne figurent plus que dans cette table.

| ancien fichier (sessions 2–3) | ancienne fonction | fichier actuel | fonction actuelle |
|---|---|---|---|
| `C_cert_lib.py` | `aire`, `enveloppe`, `oppose`, `droites`, `coupe` | `certifier/geometry.py` | `area`, `hull`, `negate`, `half_planes`, `clip` |
| | `est_convexe_strict` (virages seulement) | | `all_left_turns` ; le test **actuellement utilisé** est `is_strictly_convex` (virages + égalité à l'enveloppe, via `equals_cyclically`) |
| | `intersection`, `minkowski`, `moments`, `translate`, `cross` | | mêmes noms |
| | `aire_et_gradient`, `paralleles`, `est_regulier` | | `area_and_gradient`, `parallel_edges`, `is_regular` |
| | `dist2_origine_polygone`, `max2_origine_polygone` | | `dist2_origin_polygon`, `max2_origin_polygon` |
| | `fmpq_haut`, `fmpq_bas`, `rationnel`, `soustrait`, `nettoie` | | `fmpq_upper`, `fmpq_lower`, `rational`, `subtract`, `clean` |
| | `arb_q` | | **aucun équivalent** (appel direct à `arb`) |
| `C_cert_core.py` | `bornes_translations`, `boule`, `majorant_rayon`, `verifie` | `certifier/core.py` | `translation_bounds`, `ball`, `radius_bound`, `verify` |
| | `enumere_paires`, `actif`, `Paire.toujours` | | `enumerate_pairs`, `active`, `Pair.always` |
| | `rectangle_arc`, `borne_boite` (variable `utiliser_m2`) | | `arc_rectangle`, `box_bound` (variable `use_m2`) |
| `C_cert_config.py` | `Config` | `certifier/colourings.py` | `Config` (attribut `cell_area`) |
| `C_cert_ile.py` | construction de l'île | `certifier/island.py` | `config_ilep` et fonctions auxiliaires |
| `C_cert_run.py` | pilote | `certifier/certify.py` | `main`, `work` |
| `C_cert_relit.py` (« relit ») | recalcul à partir des JSON | `certifier/recompute.py` | `main`, `work` |
| `P_translations.py` (session 3) | `seuil` | `verifier/verify.py` | étape E4 (`smallest_k`) |
| | `separes`, `dist2` | | `strictly_separated`, `dist2` (étape E5) |
| | recomptage 394 / 1804 | | étape E5 |
| `R_verifs.py` (ce relecteur, session 3) | 1. convexité vraie (`egal_cyclique`, `hull`) | `verifier/verify.py` | étape E1 (`strictly_convex`, `same_cyclic`, `hull`) |
| | 2. inégalité clé de (a) | | étape E4 |
| | 3. recomptage | | étape E5 |
| | 4. gradient par Cyrus–Beck (`longueur_relative`) | | **aucun équivalent** dans le dépôt |
| | 5. sémantique d'Arb | | **aucun équivalent** dans le dépôt |
| journaux `P_translations_*.log`, `R_verifs_*.log`, `C_cert_*.log`, `C_relit_*.log` | | | non distribués ; les sorties équivalentes sont celles de `certifier/certify.py`, `certifier/recompute.py`, `verifier/verify.py` (`scripts/reproduce.sh`) |
| JSON `{DISQP32,ILEP256}_config.json` de la session 2 | | `certificates/{DISQP32,ILEP256}_config.json` | identiques octet pour octet (`cmp`, session 4) |

---

Fichiers relus :
- `preuves.md` (version de la session 3) ;
- les fichiers du certificateur de la session 2, aujourd'hui `certifier/geometry.py`, `certifier/core.py`, `certifier/colourings.py`, `certifier/certify.py`, `certifier/recompute.py` (lus en entier ; voir la table) ;
- le script exact des translations de la session 3, aujourd'hui étapes E4–E5 de `verifier/verify.py` (lu en entier, puis relancé) ;
- les JSON `{DISQP32,ILEP256}_config.json`, aujourd'hui `certificates/{DISQP32,ILEP256}_config.json` (identiques octet pour octet aux configurations des certificats plus fins `DISQP32_195` et `ILEP256_2032`, vérifié avec `cmp`) ;
- Gwyn–Stavrianos, arXiv:2008.07987v1, §2.1–2.4 ;
- la documentation FLINT/Arb en ligne et les docstrings de python-flint 0.9.0.

Calculs nouveaux : un script de vérification écrit par moi (session 3, non distribué ; ses contrôles 1–3 sont refaits par les étapes E1, E4, E5 de `verifier/verify.py`, ses contrôles 4–5 n'ont pas d'équivalent dans le dépôt). Toutes les exécutions ont tourné sous une limite mémoire de 1200 Mo, sans swap, avec au plus 2 processus.

## Verdict global

**Les preuves établissent la majoration certifiée : OUI sous réserve de** compléter les deux points ci-dessous. Aucun n'est DÉCISIF : chacun a été comblé dans cette relecture, par un calcul exact ou par une preuve rédigée ici.

1. **Convexité stricte des pièces (trou T1).** Le test du code (V1) ne garantit pas, à lui seul, que les pièces sont convexes. J'ai vérifié qu'elles le sont sur les données réelles : 52/52 et 260/260.
2. **Deux compléments de rédaction (T2, T5).** La mesurabilité de Jordan doit porter sur l'ensemble 3D (x, θ) de GS. Le lemme de Sutherland–Hodgman et l'étiquetage des arêtes doivent être démontrés ; je les démontre au §(iii).

Il reste par ailleurs une hypothèse de bibliothèque, standard et documentée : le principe d'inclusion d'Arb.

| point | verdict |
|---|---|
| 0.1 pavage | correct **sous réserve de T1** (comblé par calcul exact) |
| 0.2 réduction à une somme d'aires | correct ; mesurabilité de Jordan à rédiger en dimension 3 (T2, À COMPLÉTER, comblé ici) |
| (a) translations | **correct** ; calculs reproduits à l'identique, inégalité clé revérifiée indépendamment ; une coquille de signe (T3) |
| (b) filtres | **correct** ; une formulation (T4) |
| (c) A ≤ T², gradient, intégration | **correct** ; la preuve de c.4.4 dépend de SH (T5, comblé ici) ; gradient contrôlé exactement sur 800 cas indépendants |
| (d) symétrie θ → θ + π | **correct** |
| [À VÉRIFIER] (i) arb | hypothèse **standard et documentée** (principe d'inclusion de FLINT/Arb) ; sémantique des comparaisons vérifiée |
| [À VÉRIFIER] (ii) GS | réduction **correcte** ; GS est une prépublication aux preuves esquissées (T6, FORMULATION) |
| [À VÉRIFIER] (iii) SH | **démontré ici**, étiquetage compris ; la régularité est exactement ce qui est nécessaire |

(Les numéros c.4.x de cette relecture sont ceux de la session 3 ; voir la correspondance avec la numérotation actuelle de `preuves.md` dans la section finale.)

---

## 1. Calculs refaits

### 1.1 Relance du calcul exact des translations (session 3)

J'ai relu le script avant de le relancer. Il n'importe aucun fichier du certificateur et ne lit que les JSON. Les sorties sont identiques aux journaux de son auteur, ligne par ligne, à la ligne « temps » près (`diff` vide). Les temps mesurés sont de 3,2 s pour DISQP32 et 91,6 s pour ILEP256, contre 82 s annoncés.

Contrôles sur le code de ce script (aujourd'hui repris dans `verifier/verify.py`) :
- le seuil (aujourd'hui `smallest_k` dans l'étape E4) renvoie le plus petit k ≥ 1 tel que k|C| − W > 0 et (k|C| − W)² > |g|². Le test est exact et monotone en k.
- Le pré-filtre par boîtes englobantes est correct : si l'écart des boîtes est ≥ 1, alors dist ≥ 1.
- Le test de séparation (aujourd'hui `strictly_separated`) teste si une **droite d'arête elle-même** sépare strictement les deux polygones. C'est plus fort que « un axe parmi les normales », mais c'est équivalent à la disjonction : voir la preuve en T7.
- `dist2` est correct : le minimum des distances sommet–segment, dans les deux sens.

### 1.2 Vérifications indépendantes (script du relecteur, session 3)

1. **Convexité vraie.** Chaque pièce est égale, à rotation cyclique près, à son enveloppe convexe CCW. L'enveloppe est calculée en `fractions.Fraction`, sans flint. Résultat : **52/52 (DISQP32), 260/260 (ILEP256)**. (Ce contrôle est aujourd'hui l'étape E1 de `verifier/verify.py`.)
2. **Inégalité clé de (a)**, recalculée en `Fraction` (bibliothèque standard, sans flint) :
   - 2|C| − W2 > |g2| et 2|C| − W1 > |g1| sont **vrais** pour les deux colorations ;
   - marges (2|C| − W)² − |g|² : 3,9024 et 3,9024 (DISQP32), 3,8850 et 3,8141 (ILEP256) ;
   - pour |a| = 1, la projection ne conclut pas, comme annoncé.
   (Aujourd'hui étape E4 de `verifier/verify.py`.)
3. **Recomptage.** Avec |a|, |b| ≤ 1 et le critère d2 < 1 < m2, je retrouve **394** et **1804** paires, comme `core.enumerate_pairs` (|a|, |b| ≤ 2) et le script exact des translations. (Aujourd'hui étape E5 de `verifier/verify.py`.)
4. **Gradient (lemme c.4.4 de la session 3).** Le test porte sur 400 couples (paire, u0) par coloration. u0 est rationnel, régulier, avec A0 > 0, et u0 ainsi que la paire sont tirés au hasard ; la graine est fixée.
   - **Formule indépendante.** Je calcule Γ(u0) = −Σ_f n_f·λ_f par la formule du lemme c.4.1, où n_f = (dy, −dx) est l'arête f de Q et λ_f la fraction de f − u0 contenue dans P. λ_f est obtenue par découpage paramétrique de Cyrus–Beck, codé par moi, sans Sutherland–Hodgman.
   - **Comparaison.** Je la compare à la somme des arêtes d'étiquette 0 renvoyée par `area_and_gradient`. Résultat : **égalité exacte 400/400 et 400/400**.
   - **Différences finies.** Les différences finies centrées exactes (h = 2⁻³⁰) coïncident exactement (écart 0), ce qui est attendu puisque A est localement quadratique.
   - **Limite.** Les tirages aléatoires n'atteignent pas les cas dégénérés (dp = 0 exactement). Ceux-ci sont couverts par la preuve du §(iii).
5. **Sémantique d'arb** (python-flint 0.9.0, ctx.prec = 256) :
   - `arb.atan2(s, t)` est bien l'atan2(y, x) usuel : atan2(1, 0)/π = 0,5 et atan2(0, −1)/π = 1 ;
   - une boule qui chevauche la coupure renvoie `[+/- 3.15]`, ce qui reste une inclusion valide ;
   - `<` sur des boules qui se chevauchent renvoie faux dans les deux sens, et `π/2 < π/2` comme `π/2 <= π/2` sont faux : c'est la sémantique « certainement » ;
   - `man_exp()` lève `ValueError` sur une valeur infinie ou NaN, donc l'échec est franc et ne peut pas produire une borne fausse.

---

## 2. Relecture point par point

### 0.1 Pavage

L'argument est correct et l'usage de (V2) et (V3) est juste :
- f ≤ 1 hors des bords ;
- ∫_C f = Σ aire(P_i) = |C| ;
- donc f = 1 p.p.

J'ai aussi vérifié :
- `translation_bounds` donne bien le plus grand a tel que a²|C|² ≤ ρ²|g2|² ;
- `ball` fournit z_i ∈ P_i et r_i² ≥ max |v − z_i|² ;
- les sauts du cas t = 0 dans `core.verify` ne testent t = 0 que pour j > i, ce qui suffit par symétrie.

**Trou T1 (À COMPLÉTER).** (V1), c'est-à-dire le test de convexité du code de la session 2 (tous les virages consécutifs > 0, aujourd'hui `all_left_turns`), **n'implique pas la convexité**. Un pentagramme (sommets d'un pentagone régulier visités dans l'ordre 0, 2, 4, 1, 3) passe le test : tous ses virages sont à gauche, mais son nombre d'enroulement vaut 2. Toute la suite repose sur la convexité des pièces :
- l'aire par la formule du lacet doit être une mesure de Lebesgue ;
- `half_planes(Q)` doit décrire Q comme une intersection de demi-plans ;
- Sutherland–Hodgman doit être correct ;
- P_i doit être l'enveloppe de ses sommets.

La phrase de 0.1 « chaque pièce est strictement convexe (V1) » est donc fausse comme déduction. Sa conclusion est **vraie sur les données** : le contrôle §1.2.1 trouve 52/52 et 260/260.

*Correction* : on ajoute à (V1) le test « P égale son enveloppe convexe à rotation près », ou la condition équivalente « Σ des angles extérieurs = 2π ». Il suffit aussi de citer le contrôle §1.2.1. Un test simple et suffisant est cross(P_0, P_k, P_{k+1}) > 0 pour tout k, combiné à la condition de virage.

### 0.2 Réduction à une somme d'aires

La proposition 0.2 est correcte :
- on intègre sur F, domaine fondamental p.p. ;
- on décompose selon l'unique pièce qui contient x et l'unique translaté qui contient x + u ;
- on conclut par convergence monotone et finitude.

J'ai vérifié que `core.enumerate_pairs` **inclut** les couples (i, i, t = 0), c'est-à-dire P avec lui-même : il n'y a pas de saut à t = 0. Voir T2 pour la définition GS.

### (a) Complétude des translations

- **Lemme a.1** : correct, et c'est ce dont le code a besoin.
- **Théorème a.2** : correct. J'ai revérifié indépendamment l'inégalité qui l'établit (§1.2.2).
- **T3 (FORMULATION).** Étape 2 de la partie 1 : comme y = y' + t, on a t = (y − x) − (y' − x). La bonne formule est donc **det(g2, t) = det(g2, y − x) − det(g2, y' − x)**, et non une somme. La majoration |a|·|C| ≤ W2 + |g2| est inchangée.
- **Remarque.** La partie 2 (distances exactes, recomptage 394/1804) n'est pas nécessaire à la correction du code. Le lemme a.1 suffit pour l'énumération |a|, |b| ≤ 2, et la partie 1 suffit pour |a|, |b| ≤ 1. La partie 2 n'est qu'un recoupement. L'affirmation « (±1, ±1) de même signe : aucun couple de même couleur à distance < 1 » repose sur le pré-filtre par boîtes, qui donne dist ≥ 1. Cela suffit, puisque d2 ≥ 1 élimine la paire (b.2).

### (b) Filtres des paires

- **Lemme b.1 et proposition b.2** : corrects. Le cas d2 = 1 exactement est bien traité : un point de int M ne peut pas être de norme 1 si dist(0, M) = 1.
- **`dist2_origin_polygon`** : correct, puisque M sort de `hull` et est strictement convexe CCW, avec au moins 3 sommets.
- **Lemme b.3** : correct, et la quasi-linéarité de tan β est bien utilisée.
- **Proposition b.3** : correcte. J'ai refait le calcul des valeurs de k : 2πk = θ − (φ + α) ∈ (−2π, 3π), d'où k ∈ {0, 1}. Les décalages {−4, …, 4} en unités de π couvrent largement ces cas.
- **T4 (FORMULATION).** Étape 1 : « u ∈ M, donc d2 > 0 » est mal dit. d2 > 0 vient de ce que `active` est faux, ce qui force `always` faux, donc d2 ≠ 0. L'appartenance u ∈ M sert seulement au lemme b.3.

### (c) Lemme A ≤ T² et majoration d'une boîte

- **c.1–c.3** : corrects.
  - Brunn–Minkowski s'applique à des compacts non vides d'aire > 0.
  - La concavité de φ sur [0, 1] utilise u0, u ∈ S, avec S convexe et ouvert, donc φ'(0) est la dérivée directionnelle.
  - Le cas u ∉ S est trivial.
- **c.4.1–c.4.3** : corrects.
  - J'ai revérifié le signe de la formule de Gauss–Green sur le carré unité avec u = (ε, 0) : ∇A_x = −1. L'identité 1_P(y − u) = 1_{−P}(u − y) est juste.
  - La continuité des extrémités de corde vient de leur concavité ou convexité en le décalage.
  - Le cas d'une droite d'appui passe par la semi-continuité supérieure.
- **Test codé de la régularité** : correct.
  - `parallel_edges` normalise c_Q = c2/k, ce qui est juste y compris pour k < 0.
  - `is_regular` est exactement la condition de régularité.
- **c.4.4** : correct **une fois démontré le lemme de SH** (T5, comblé au §(iii)). Le contrôle exact du §1.2.4 donne 800/800.
- **c.5–c.7** : corrects. J'ai revérifié :
  - les primitives (`moments`) : I_cs = (sin²t1 − sin²t0)/2 et I_cc = h/2 + (sin 2t1 − sin 2t0)/4 ;
  - les moments centrés J ;
  - la forme de B, avec (G·d)² = gx²dx² + 2gx·gy·dx·dy + gy²dy² ;
  - `arc_rectangle`, qui utilise la décroissance de cos, la concavité de sin et le branchement sur `t1 < π/2`. Ce test « certainement vrai » renvoie à défaut yhi = 1, ce qui est sûr ;
  - (M2), par Q − u ⊆ Q ⊕ (−K) ;
  - la partition exacte des boîtes (vérifiée par le recalcul, aujourd'hui `certifier/recompute.py`) ;
  - la normalisation.
- **Remarque.** `use_m2 = (A0 == 0)` couvre aussi les cas `len(S) < 3`. Le choix flottant entre (M1) et (M2) n'a pas d'effet sur la validité. Les journaux de session 2 confirment « essais u0 > 0 : 0 » pour DISQP32 et ILEP256, et le recalcul (aujourd'hui `certifier/recompute.py`) confirme 0,0051864759 et 0,0049233542.

### (d) Symétrie

Correct : τ(E(u)) = E(−u) et τ préserve la mesure de Haar du tore. L'étape 3 n'apporte rien ; on peut la supprimer. La normalisation 1/(π|C|) est juste.

---

## 3. Les trois points [À VÉRIFIER]

### (i) Sémantique d'inclusion des boules arb

**Documentation officielle de FLINT/Arb** (module arb.h, <https://flintlib.org/doc/arb/index.html>) :
- « Every function in this module satisfies the inclusion principle: if each input ball contains some real number, the output ball contains the exact result of the operation applied to those numbers. »
- `arb_atan2` : argument de a + bi, dans (−π, π], avec la coupure sur (−∞, 0].
- `arb_lt` et `arb_gt` renvoient 1 si la relation vaut pour **tous** les points des boules.
- `arb_get_ubound_arf` donne l'extrémité droite arrondie vers le haut.

**Docstrings de python-flint 0.9.0** :
- `arb.upper()` est « an exact floating-point number that has been rounded up » ; `lower()` est arrondi vers le bas ;
- `man_exp()` « requires that self is exact and finite » et lève une erreur sinon.

**Ce que la documentation de python-flint ne dit pas explicitement** : le principe d'inclusion de ses enveloppes et la sémantique de `<`. Il s'agit cependant d'enveloppes directes des fonctions Arb, et la sémantique de `<` correspond à `arb_lt`. Je l'ai vérifiée empiriquement (§1.2.5).

**Verdict** : l'hypothèse est **standard et documentée** au niveau d'Arb, qui est la bibliothèque de référence de l'arithmétique de boules rigoureuse. Elle reste une confiance accordée à l'implémentation ; c'est le niveau habituel des preuves assistées par Arb. Une erreur de python-flint sur `man_exp`, inf ou NaN ferait échouer le calcul ; elle ne fausserait pas la borne.

### (ii) Définition de p_k chez Gwyn–Stavrianos et lemme 2.10 (relu dans le texte)

**Définitions 2.4–2.7.**
- p_k(c) = E_{c*}[b_{c*}(0, 1)] = µ_T{T ∈ E(2) : c(T(0)) = c(T(1))}, où µ_T est une moyenne finiment additive, invariante des deux côtés, sur **toutes** les parties de E(2) ;
- p_k = inf_c p_k(c).

**Lemme 2.10.** Si G est un graphe fini de distance unité non k-colorable, alors p_k ≥ 1/|E(G)|. La preuve est correcte dans ce cadre :
- B = Σ_e b_{c*}(e) ;
- E[B] = |E|·p_k(c), par linéarité et invariance par isométrie ;
- B ≥ 1 partout, puis lemme 2.8.

La conséquence utilisée est la suivante : tout graphe de distance unité non 5-colorable a au moins 1/p5 ≥ 1/p5(c) arêtes. C'est bien la chaîne visée.

**Théorèmes 2.17–2.22.**
- Pour une coloration périodique, p_k(c) = µ_J(S) avec S = {(x, θ) ∈ R(z1, z2) × [0, 2π) : c(x) = c(x + e^{iθ})}, où µ_J est la mesure de Jordan normalisée à 1. Cela vaut **si S est Jordan-mesurable**.
- Par Riemann ⇒ Lebesgue puis Fubini, on obtient p_k(c) = (1/2π)∫_0^{2π} |C|⁻¹ mes{x ∈ C : c(x) = c(x + u(θ))} dθ.
- C'est exactement la définition utilisée en 0.2. Le choix de la cellule (le parallélogramme demi-ouvert de GS ou la cellule fermée C) est sans effet, à un ensemble nul près.

**T2 (À COMPLÉTER).** 0.2 justifie la Jordan-mesurabilité de « l'ensemble monochrome » par des bords en segments dans le plan. Or GS exige la Jordan-mesurabilité de S **dans l'espace 3D** des (x, θ). Je propose une preuve.
1. S est borné. Sa frontière (dans R̄ × [0, 2π]) est contenue dans ∂(R̄ × [0, 2π]) ∪ {(x, θ) : x ∈ Z} ∪ {(x, θ) : x + u(θ) ∈ Z}, où Z est la réunion des bords des translatés P_i + g. Ces bords sont en nombre fini près du compact.
2. Chacun de ces trois ensembles est compact (à l'intérieur d'un compact) et de mesure de Lebesgue nulle. Le troisième est une réunion finie d'images lipschitziennes de [0, 1] × [0, 2π] dans ℝ³, c'est-à-dire de surfaces.
3. Un compact de mesure nulle est de contenu de Jordan nul, donc S est Jordan-mesurable.

Il faut aussi que **c soit une vraie fonction G-périodique sur tout le plan**, ce que GS exige (définition 2.16). « Les bords reçoivent une couleur arbitraire » doit être précisé. Par exemple, x prend la couleur de la pièce de plus petit indice i telle que x ∈ P_i + G ; cette règle est G-périodique par construction.

**T6 (FORMULATION ; ne met pas la réduction en cause).** GS est une prépublication arXiv (v1, 2020) dont je n'ai pas vérifié la publication. Ses preuves 2.18–2.21 sont esquissées :
- « strictly increasing » n'est pas justifié ; seule la monotonie sert, et elle découle de l'additivité ;
- ϕ n'est pas une bijection, puisque E(2) contient les réflexions et que ϕ est donc 2 à 1. C'est sans conséquence, car b_c ne dépend que de (T(0), T(1)) ;
- l'invariance par translation non entière modulo L n'est pas détaillée.

Le résultat est néanmoins juste et classique : une moyenne invariante sur le quotient compact L\E(2) coïncide avec la mesure de Haar sur les ensembles Jordan-mesurables. On encadre par des réunions finies de « boîtes » translatées, et l'invariance force la valeur de chaque boîte. Je recommande de citer ce fait sous cette forme plutôt que de s'appuyer seulement sur les preuves de GS.

**Verdict (ii)** : la réduction est **correcte**, y compris la périodicité et la normalisation, sous réserve de rédiger T2 comme ci-dessus.

### (iii) Sutherland–Hodgman et étiquetage des arêtes : démonstration

On considère `clip(X, tags, a, b, c, τ)` (`certifier/geometry.py`) : la liste X = (x_0, …, x_{n−1}) parcourt, dans le sens direct, le bord d'un polygone convexe K d'aire > 0, en admettant des sommets répétés et des sommets alignés. Chaque arête x_i → x_{i+1} est contenue dans une droite D(tags[i]) associée à son étiquette. On pose d(x) = a·x + b·y − c et H = {d ≤ 0}.

**Lemme SH.** Si K ∩ H est d'aire > 0, alors la sortie parcourt ∂(K ∩ H) dans le sens direct, sans retour en arrière. Chaque arête de longueur > 0 de la sortie est :
- soit un sous-segment d'une arête d'entrée, avec la même étiquette ;
- soit un segment de la droite d = 0, avec l'étiquette τ.

*Preuve.*
1. **Unimodalité.** Paramétrons ∂K par une courbe fermée γ, parcourue dans le sens direct. Une fonctionnelle linéaire restreinte au bord d'un convexe est unimodale : il existe deux arcs, l'un où elle atteint son maximum, l'autre son minimum (ce sont des faces), et elle est monotone sur les deux arcs qui les relient. Donc {s : d(γ(s)) ≤ 0} est un arc fermé connexe Γ₋ (ou le cercle entier), et {d > 0} est l'arc ouvert complémentaire Γ₊.
2. **Cas Γ₊ = ∅.** Le code recopie la liste avec ses étiquettes : il prend la branche `dp <= 0` et `dq <= 0` à chaque arête. La sortie est ∂K = ∂(K ∩ H).
3. **Cas Γ₊ ≠ ∅.**
   - Le long de Γ₋, chaque sommet de la liste est émis, avec l'étiquette de l'arête qui en part. Cette arête est une arête d'entrée, ou un sous-segment d'arête d'entrée si le sommet suivant émis est le point de sortie.
   - L'unique arête p → q avec d(p) ≤ 0 < d(q) émet p, puis le point de sortie s = p + t(q − p), avec t = dp/(dp − dq) ∈ [0, 1), sur d = 0, étiqueté τ.
   - Les arêtes entièrement dans Γ₊ n'émettent rien.
   - L'unique arête p → q avec d(p) > 0 ≥ d(q) émet le point d'entrée e ∈ [p, q], d(e) = 0, avec l'étiquette de p → q. L'arête suivante de la sortie est e → q, sous-segment de p → q, puisque q est émis à l'itération suivante.
   - L'arête s → e de la sortie est donc portée par d = 0 et étiquetée τ. C'est la corde K ∩ {d = 0}, puisque s et e sont les deux points de ∂K sur la droite, Γ₊ étant un arc. ∂(K ∩ H) est exactement Γ₋ suivi de la corde [s, e], dans le sens direct : l'intérieur reste à gauche, car K ∩ H est à gauche de chaque arête de Γ₋ et du côté d ≤ 0 de la corde.
4. **Raccord cyclique.** Il est correct. Le cas où x_0 est dehors est traité par le premier point d'entrée émis ; le cas où le dernier sommet émis précède x_0 l'est par la cyclicité de la liste.
5. **Cas limites.**
   - d(p) = 0 avec d(q) > 0 donne t = 0, donc s = p dupliqué.
   - d(q) = 0 avec d(p) > 0 donne t = 1, donc e = q dupliqué.
   - Les arêtes de longueur nulle ainsi créées contribuent (0, 0) au gradient.
   - Une arête portée par la droite d = 0 (dp = dq = 0) est recopiée avec **son ancienne étiquette**. Ce cas est examiné ci-dessous. ∎

**Application à `intersection(P, Q − u0)`, A0 > 0.**
1. Toutes les étapes intermédiaires sont d'aire > 0, puisqu'elles contiennent le résultat final. Le lemme s'applique donc à chaque étape, en partant de P, convexe CCW strict par T1 comblé.
2. Par récurrence, chaque arête de longueur > 0 du résultat est portée :
   - si elle est d'étiquette 0, par la droite d'une arête de P ;
   - si elle est d'étiquette 1, par la droite L_f d'une arête f de Q − u0.
3. **Seul cas délicat** (5, dernier point). Une arête déjà présente est portée par la nouvelle droite de coupe L_f et garde son ancienne étiquette.
   - Si l'étiquette est 0, une arête de P est portée par L_f. La **régularité l'exclut**, et c'est exactement le rôle de `is_regular`.
   - Si l'étiquette est 1, la droite d'une autre arête f' de Q − u0 coïncide avec L_f. C'est impossible, car Q = P_j + t est strictement convexe (T1) et ses arêtes ont des droites distinctes.
   - En u0 régulier, les arêtes de longueur > 0 sur L_f sont donc toutes étiquetées 1, et réciproquement.
4. Le parcours est direct, simple et sans retour. La somme des longueurs des arêtes de ∂I portées par L_f vaut donc longueur(I ∩ L_f) = ℓ_f(u0). Chacune a (dy, −dx) = |e|·ν_f, puisque I ⊆ {ν_f·x ≤ c_f}.
5. Le télescopage Σ (dy, −dx) = 0 donne G = −Σ_f ν_f·ℓ_f(u0) = Γ(u0).

C'est la preuve c.4.4, désormais complète.

**Ce qui manquait dans `preuves.md`** : l'unimodalité qui fonde SH, l'absence de retour en arrière (qui suppose A0 > 0), et le traitement explicite d'une arête recopiée sur la droite de coupe. C'est là qu'interviennent la régularité et la convexité stricte de Q.

La même preuve valide `intersection` dans `core.verify` (V3). Le cas d'aire nulle n'y pose pas de problème : seule l'aire est utilisée, et l'aire du lacet d'un parcours dégénéré, de longueur nulle ou sur un segment, vaut 0, puisque l'intersection est alors d'intérieur vide.

**Verdict (iii)** : démontré.

---

## 4. Liste des trous

| n° | lieu | nature | gravité | correction |
|---|---|---|---|---|
| T1 | 0.1, (V1) | le test de convexité de la session 2 (virages seulement, aujourd'hui `all_left_turns`) accepte des polygones étoilés (enroulement 2) ; la convexité est utilisée partout | **À COMPLÉTER** (vrai sur les données : 52/52, 260/260, contrôle §1.2.1) | ajouter un test d'égalité à l'enveloppe convexe dans `core.verify` (donc aussi dans le recalcul), ou citer le contrôle §1.2.1 |
| T2 | 0.2 | la Jordan-mesurabilité exigée par GS porte sur S ⊂ ℝ² × [0, 2π], pas sur le plan ; la coloration des bords doit être une fonction G-périodique | **À COMPLÉTER** | argument du §(ii) : frontière dans une réunion finie de compacts négligeables ; règle « plus petit indice » |
| T3 | (a), a.2, partie 1, étape 2 | signe : det(g2, t) = det(g2, y − x) − det(g2, y' − x) | FORMULATION | corriger ; la borne est inchangée |
| T4 | (b), prop. b.3, étape 1 | « u ∈ M donc d2 > 0 » : d2 > 0 vient de `always` faux | FORMULATION | reformuler |
| T5 | (c), c.4.4 | le lemme SH et la gestion des étiquettes étaient admis | **À COMPLÉTER** (comblé au §(iii)) | insérer la preuve du §(iii) |
| T6 | 0.2 / GS | GS est une prépublication aux preuves esquissées ; ϕ est 2 à 1 (réflexions) | FORMULATION | citer le fait classique (moyenne invariante = Haar sur les Jordan-mesurables) |
| T7 | (a), partie 2, test de séparation (aujourd'hui `strictly_separated`) | « axe parmi les normales d'arêtes » : le code teste la droite d'arête elle-même | FORMULATION | preuve : si P ∩ Q = ∅, 0 ∉ M = Q − P ; une arête de M sépare strictement 0. Elle est parallèle à une arête e de Q (ou de −P) de même normale sortante n, et 0 > h_Q(n) − min_P⟨n, ·⟩, donc P est strictement au-delà de la droite de e. La partie 2 n'est de toute façon pas nécessaire |
| T8 | (i) | le principe d'inclusion n'est documenté qu'au niveau d'Arb, pas dans la documentation de python-flint | FORMULATION (hypothèse standard) | citer la documentation FLINT/Arb et la vérification empirique du §1.2.5 |
| T9 | (d), étape 3 | phrase sans contenu | FORMULATION | supprimer |

**Aucun trou DÉCISIF.**

## 5. Conclusion

**Les preuves établissent la majoration certifiée : OUI, sous réserve de** trois éléments :
1. **(T1)** La convexité vraie des pièces, qui n'est pas impliquée par le test du code. Je l'ai vérifiée exactement sur les deux colorations certifiées ; il faut l'intégrer au certificat ou à la rédaction.
2. **(T2, T5)** Les deux compléments de rédaction fournis aux §(ii) et §(iii) : la Jordan-mesurabilité en (x, θ), avec une coloration périodique définie partout, et le lemme de Sutherland–Hodgman avec son étiquetage.
3. **L'hypothèse de bibliothèque** : le principe d'inclusion d'Arb, standard et documenté.

Cela porte sur les bornes p5(DISQP32) ≤ 0,0051864759 et p5(ILEP256) ≤ 0,0049233542 recalculées par le recalcul (aujourd'hui `certifier/recompute.py`), et sur les bornes annoncées par les certificats `_195` et `_2032` (mêmes JSON de configuration). La correction des certificats eux-mêmes, c'est-à-dire la sommation des boîtes, est hors du champ de cette relecture ; le recalcul la refait.

---

## Mise à jour du 15 novembre 2026 (session 4)

**Pourquoi.** Un audit externe n'a trouvé aucune erreur mathématique, mais a demandé que ce document et `preuves.md` décrivent le **code distribué** (commit `3af8dfe` ; le code de `certifier/` et `verifier/` n'a pas changé depuis), et qu'ils puissent être publiés dans le dépôt. La version de la session 3 de ce document est conservée à part, sans modification.

**Ce qui a été changé dans ce document.**
1. Ajout de la table de correspondance en tête et de cette section.
2. Dans les sections 1 à 5, les noms d'anciens fichiers et d'anciennes fonctions ont été remplacés par les fichiers et fonctions actuels (ou, pour les scripts de session 3 sans équivalent, par une description : « script du relecteur, session 3, non distribué »). Les numéros de ligne ont été supprimés.
3. Les chemins locaux de la machine de travail (JSON, texte de GS, journaux, commandes d'exécution) ont été retirés ou remplacés par des chemins relatifs au dépôt ou par la référence arXiv.
4. **Les verdicts, la liste des trous T1–T9 et la conclusion sont inchangés.** Ils décrivent l'état du code et de `preuves.md` au 14 novembre 2026.

**Suite donnée aux trous (état au 15 novembre 2026).**
- **T1 — corrigé dans le code.** Le test de convexité du code distribué est `is_strictly_convex` (`certifier/geometry.py`) : `all_left_turns(P)` **et** `equals_cyclically(list(P), hull(P))`, c'est-à-dire virages positifs et égalité, à rotation cyclique près, avec l'enveloppe convexe (chaîne monotone, sans points alignés). Il est appelé par `core.verify`, donc par `certifier/certify.py` et `certifier/recompute.py`. Le vérificateur indépendant fait le même test en `Fraction` (étape E1 de `verifier/verify.py`, fonction `strictly_convex`). Un pentagramme est rejeté. `preuves.md`, §0.0, démontre que ce test garantit la convexité stricte (lemme 0.0).
- **T2 — intégré.** `preuves.md`, §0.1–0.2, renvoie au §(ii) ci-dessus pour la Jordan-mesurabilité en (x, θ) et adopte la règle « plus petit indice » pour la couleur des bords, qui est aussi celle du README.
- **T3 — corrigé.** `preuves.md`, théorème a.2, partie 1, étape 2 : det(g2, t) = det(g2, y − x) − det(g2, y' − x), car t = (y − x) − (y' − x). Vérifié à nouveau en session 4 à partir des définitions ; la majoration en valeur absolue est inchangée.
- **T4 — corrigé.** `preuves.md`, proposition b.3, étape 1 : `active` faux ⇒ `pr.always` faux ⇒ la paire a été construite dans la branche `else` du test `if d2 == 0` de `core.enumerate_pairs` ⇒ d2 > 0, donc 0 ∉ M (le test `inside` de `dist2_origin_polygon` a échoué). u ∈ M ne sert qu'au lemme b.3.
- **T5 — intégré, et preuve du gradient refaite.** `preuves.md`, §c.4, donne désormais une preuve directe de la formule ∇A(u0) = −Σ_f ν_f |f ∩ P| (identité exacte d'accroissement par comptage des traversées, continuité des longueurs ℓ_f sous l'hypothèse de régularité vérifiée par `is_regular`), puis le lien avec l'étiquetage de `clip`/`intersection`/`area_and_gradient` (étiquette 0 : arêtes portées par ∂P ; étiquette 1 : arêtes portées par ∂(Q − u0)), en s'appuyant sur le lemme SH du §(iii).
- **T6, T8 — intégrés** sous forme de références ([CONNU + …]) et de points [À VÉRIFIER] dans `preuves.md`, §0.2 et §6.
- **T7 — intégré.** `preuves.md`, (a), partie 2, décrit `strictly_separated` (`verifier/verify.py`) et renvoie à T7.
- **T9 — non appliqué.** L'étape 3 de la proposition d.1 est conservée ; elle est sans contenu mais sans danger.

**Correspondance de numérotation avec `preuves.md` (version actuelle).** Les numéros c.4.x de cette relecture renvoient à la version de la session 3 : ancien c.4.1 (gradient distributionnel) → c.4.1–c.4.3 (identité exacte d'accroissement) ; ancien c.4.2 (continuité) → c.4.4 ; ancien c.4.3 (différentiabilité) → c.4.5 ; ancien « test codé » → c.4.6 ; ancien c.4.4 (ce que calcule le code) → c.4.7. Un nouveau §0.0 (test de convexité) a été ajouté.

**Certificats.** Les certificats distribués, `certificates/{DISQP32,ILEP256}_certificat.json` (256 et 1024 boîtes), sont identiques octet pour octet à ceux dont le recalcul de la session 3 a confirmé les bornes 0,0051864759 et 0,0049233542 (`cmp`, session 4). Les certificats plus fins `_195` et `_2032` (2048 boîtes) cités dans la conclusion ne sont pas distribués et ne sont pas revendiqués par le dépôt.

**Contrôles de session 4** [VÉRIFIÉ NUMÉRIQUEMENT ; fonctions du dépôt utilisées sans modification, script non distribué] : pentagramme rejeté par `is_strictly_convex` (mais accepté par `all_left_turns`) ; identité de signe de T3 juste sur 1000 tirages rationnels exacts (la version « somme » est fausse sur les 1000) ; `area_and_gradient` égal exactement à −Σ_f n_f λ_f (Cyrus–Beck indépendant) sur 294 couples de polygones rationnels aléatoires en position régulière, étiquettes cohérentes dans les 294 cas ; identité exacte d'accroissement de `preuves.md`, c.4.3, vérifiée à 10⁻⁸ près (erreur de quadrature) pour un grand accroissement.
