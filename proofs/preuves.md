# Preuves écrites de la certification de p5 (problème 3, session 3, point 1 ; mis à jour en session 4)

Objet : démontrer les étapes de la certification **telles que le code distribué les exécute**. Le code de référence est celui du dépôt distribué, au commit `3af8dfe` (le code de `certifier/` et `verifier/` n'a pas changé depuis ce commit) :

- `certifier/geometry.py` (géométrie exacte des polygones convexes, aides Arb) ;
- `certifier/core.py` (vérifications exactes, énumération des paires, majoration d'une boîte) ;
- `certifier/colourings.py`, `certifier/island.py` (constructions des colorations) ;
- `certifier/certify.py` (pilote de la certification), `certifier/recompute.py` (recalcul à partir des JSON) ;
- `verifier/verify.py` (vérificateur **indépendant** : il n'importe pas le certificateur et n'utilise pas python-flint) ;
- les colorations exactes `certificates/{DISQP32,ILEP256}_config.json` et les certificats `certificates/{DISQP32,ILEP256}_certificat.json`.

Les renvois sont faits par **fonction** (`fichier.py`, `fonction`), et non par numéro de ligne. Rédaction initiale : session 3 (2026-11-14) ; mise à jour : session 4 (2026-11-15), voir la dernière section.

## Table de correspondance « ancien fichier/fonction → fichier/fonction actuels »

La rédaction de la session 3 renvoyait aux fichiers de travail des sessions 2 et 3. Ils ont été renommés et traduits pour le dépôt distribué. Les anciens noms ne figurent plus que dans cette table.

| ancien fichier (sessions 2–3) | ancienne fonction | fichier actuel | fonction actuelle |
|---|---|---|---|
| `C_cert_lib.py` (« lib ») | `aire` | `certifier/geometry.py` | `area` |
| | `translate`, `cross`, `minkowski`, `intersection`, `moments` | | mêmes noms |
| | `enveloppe` | | `hull` |
| | `est_convexe_strict` (virages seulement) | | `all_left_turns` ; le **test réellement utilisé** est maintenant `is_strictly_convex` (virages + égalité à l'enveloppe, via `equals_cyclically`), sans équivalent dans l'ancien fichier |
| | `oppose` | | `negate` |
| | `droites` | | `half_planes` |
| | `coupe` | | `clip` |
| | `aire_et_gradient` | | `area_and_gradient` |
| | `paralleles` | | `parallel_edges` |
| | `est_regulier` | | `is_regular` |
| | `dist2_origine_polygone`, `max2_origine_polygone` | | `dist2_origin_polygon`, `max2_origin_polygon` |
| | `soustrait`, `nettoie` | | `subtract`, `clean` |
| | `fmpq_haut`, `fmpq_bas` | | `fmpq_upper`, `fmpq_lower` |
| | `rationnel` | | `rational` |
| | `arb_q` | | **aucun équivalent** (c'était `arb(x)` ; le code actuel appelle `arb` directement) |
| `C_cert_core.py` (« core ») | `bornes_translations` | `certifier/core.py` | `translation_bounds` |
| | `boule`, `majorant_rayon` | | `ball`, `radius_bound` |
| | `verifie` | | `verify` |
| | `Paire` (attribut `toujours`) | | `Pair` (attribut `always`) |
| | `angle_arb` | | `angle_arb` |
| | `enumere_paires` | | `enumerate_pairs` |
| | `actif`, `actif_f` | | `active`, `active_float` |
| | `F_flottant`, `p_flottant` | | `F_float`, `p_float` |
| | `rectangle_arc` | | `arc_rectangle` |
| | `borne_boite` (variable `utiliser_m2`, paramètre `seuil_quad`) | | `box_bound` (variable `use_m2`, paramètre `quad_threshold`) |
| `C_cert_config.py` | `Config` (attribut `aire_cellule`) | `certifier/colourings.py` | `Config` (attribut `cell_area`) |
| | `hexagone`, `reseau_hex`, `hexagones_reps`, `ajoute_cinquieme` | | `hexagon`, `hex_lattice`, `hexagon_reps`, `add_fifth_colour` |
| | `config_bandes`, `config_h4`, `ngone`, `config_disqp`, `construit` | | `config_strips`, `config_h4`, `ngon`, `config_disqp`, `build` |
| `C_cert_ile.py` | (construction de l'île) | `certifier/island.py` | `config_ilep` et fonctions auxiliaires |
| `C_cert_run.py` (« run ») | `travail`, `main` | `certifier/certify.py` | `work`, `main` |
| `C_cert_relit.py` (« relit ») | `travail`, `main` | `certifier/recompute.py` | `work`, `main` |
| `P_translations.py` (session 3) | `seuil` | `verifier/verify.py` | étape E4 (`smallest_k` appliqué à la condition k\|C\| − W > 0 et (k\|C\| − W)² > \|g\|²) |
| | `separes`, `dist2`, `hull`, `d2_point_segment` | | `strictly_separated`, `dist2`, `hull`, `d2_point_segment` (étape E5) |
| | `seuil_diam` (seuil grossier par le diamètre) | | **aucun équivalent** |
| | calcul des distances minimales par translation, toutes couleurs | | **aucun équivalent** (E5 ne traite que les paires de même couleur avec \|a\|, \|b\| ≤ 1) |
| `R_verifs.py` (relecture, session 3) | convexité vraie (`egal_cyclique`, `hull`) | `verifier/verify.py` | étape E1 (`strictly_convex`, `same_cyclic`, `hull`) |
| | inégalité clé de (a) | | étape E4 |
| | recomptage 394 / 1804 | | étape E5 |
| | contrôle du gradient par Cyrus–Beck (`longueur_relative`) | | **aucun équivalent** dans le dépôt |
| | contrôles de la sémantique d'Arb | | **aucun équivalent** dans le dépôt |
| journaux `C_cert_*.log`, `C_relit_*.log`, `P_translations_*.log` | | | sorties de `certifier/certify.py`, `certifier/recompute.py`, `verifier/verify.py` (non distribuées ; à régénérer par `scripts/reproduce.sh`) |
| colorations `{DISQP32,ILEP256}_config.json` de la session 2 | | `certificates/{DISQP32,ILEP256}_config.json` | identiques octet pour octet (contrôlé par `cmp` en session 4) |

## Bilan

| point | énoncé | statut |
|---|---|---|
| 0.0 | le test de convexité du code (`is_strictly_convex`) garantit la convexité stricte | [DÉMONTRÉ ICI], modulo la correction de la chaîne monotone d'Andrew [CONNU + Andrew 1979] |
| 0.1 | les translatés des pièces pavent le plan p.p. (à partir de ce que vérifie `core.verify`) | [DÉMONTRÉ ICI] |
| 0.2 | p5(c) = (1/(π\|C\|)) ∫_0^π Σ A_PQ(u(θ)) dθ | [DÉMONTRÉ ICI] (sous la définition de p_k de Gwyn–Stavrianos, voir 0.2) |
| (a) | translations : seules \|a\| ≤ 1 et \|b\| ≤ 1 peuvent porter un couple de points à distance ≤ 1. L'énumération du code (\|a\|, \|b\| ≤ 2) est donc complète | [DÉMONTRÉ ICI] (preuve + calcul exact) |
| (b) | le filtre des paires (dist < 1 < max) et le filtre angulaire par boîte n'éliminent que des paires de contribution nulle | [DÉMONTRÉ ICI] |
| (c) | (M1) A ≤ T² partout ; formule du gradient ∇A(u0) = −Σ_f ν_f \|f ∩ P\| et lien avec l'étiquetage de Sutherland–Hodgman ; (M2) ; intégration en Arb | [DÉMONTRÉ ICI], modulo la sémantique d'inclusion d'Arb [CONNU + documentation FLINT/Arb] et Brunn–Minkowski [CONNU + Gardner 2002] |
| (d) | symétrie θ → θ + π et normalisation 1/(π\|C\|) | [DÉMONTRÉ ICI] |

Je n'ai trouvé aucune divergence de fond entre le code et la rédaction de la certification (session 2 ; sa version actuelle, condensée, est la section 4 de `note/v6_45.tex`). Les différences de détail sont listées au §5.

---

## Notations et conventions (vérifiées dans le code)

- **Réseau.** G = ℤg1 + ℤg2, avec g1 = (3R, s) et g2 = (0, 2s) rationnels (JSON). La cellule C est le parallélogramme engendré par g1, g2 et |C| = |det(g1, g2)|. Ce nombre est calculé par `Config.__init__` (`certifier/colourings.py`, attribut `cell_area`) ; `certifier/recompute.py` vérifie qu'il est égal au champ `aire_cellule` des deux JSON, et `verifier/verify.py` (étape E2) le vérifie indépendamment.
- **Pièces.** P_1, …, P_N sont des polygones convexes à sommets rationnels, dans le sens direct (CCW), chacun muni d'une couleur c_i ∈ {0, …, 4}. On a N = 52 pour DISQP32 et N = 260 pour ILEP256. On note F = ∪ P_i.
- **Paire.** Une paire est (P, Q) avec P = P_i et Q = P_j + t, où t = a·g1 + b·g2 et c_i = c_j (`core.enumerate_pairs` : `Q = L.translate(Q0, t)`).
- **Aire de recouvrement.** u(θ) = (cos θ, sin θ) et

  A_PQ(u) = aire(P ∩ (Q − u)) = mes{x ∈ P : x + u ∈ Q}.

  **Convention de signe vérifiée** : `area_and_gradient(P, Q, u)` (`certifier/geometry.py`) calcule `Qu = translate(Q, (−u[0], −u[1]))`, puis `intersection(P, Qu)`. C'est donc bien aire(P ∩ (Q − u)), le point x étant dans P et x + u dans Q.
- **Support.** M = Q − P = Q ⊕ (−P) = {q − p}. Le code l'obtient par `L.minkowski(Q, L.negate(P))` (`core.enumerate_pairs`), enveloppe convexe exacte (`hull`) des différences de sommets.
- **Boîtes.** Une boîte est I = [x0·π, x1·π], avec x0 < x1 rationnels dans [0, 1].
- **Normales.** Pour une arête f d'un polygone CCW, ν_f désigne la normale sortante **unitaire** ; le code manipule n_f := (dy, −dx) = |f|·ν_f (normale sortante de longueur |f|). La note écrit n_f pour la normale unitaire ν_f.

---

## 0.0 Le test de convexité réellement utilisé [DÉMONTRÉ ICI]

**Ce que fait le code.** `core.verify` appelle, pour chaque pièce, `is_strictly_convex(P)` (`certifier/geometry.py`), qui vaut

  `all_left_turns(P)` **et** `equals_cyclically(list(P), hull(P))`,

où :
- `all_left_turns(P)` : n ≥ 3 et cross(P_i, P_{i+1}, P_{i+2}) > 0 pour tout i (indices modulo n) ;
- `hull(P)` : enveloppe convexe par la chaîne monotone d'Andrew, sur l'ensemble `set(P)` des sommets, renvoyée dans le sens direct **sans points alignés** (les tests `cross(...) <= 0` retirent les points alignés) ;
- `equals_cyclically(P, H)` : P et H ont la même longueur et P est une rotation cyclique de H.

Le vérificateur indépendant fait le même test, réécrit en `fractions.Fraction` : étape E1 de `verifier/verify.py`, fonction `strictly_convex` (avec ses propres `hull` et `same_cyclic`).

**Lemme 0.0.** Si `is_strictly_convex(P)` est vrai, alors les sommets de P sont deux à deux distincts, la liste P est exactement la liste des points extrémaux de conv(P) dans le sens direct, et la ligne polygonale fermée P_0 → P_1 → … → P_{n−1} → P_0 est le bord de conv(P), parcouru une seule fois dans le sens direct. En particulier P est un polygone strictement convexe (tous ses angles sont < π) et P = conv(sommets).

*Preuve.*
1. [CONNU + A. M. Andrew, *Another efficient algorithm for convex hulls in two dimensions*, Inform. Process. Lett. 9 (1979) 216–219.] Pour un ensemble fini S de points non tous alignés, la chaîne monotone, avec les tests de virage « ≤ 0 », renvoie la liste des points extrémaux de conv(S) dans le sens direct, chacun une fois. Si S est aligné, elle renvoie au plus 2 points.
2. `equals_cyclically` exige len(P) = len(hull(P)). Comme hull(P) est calculé sur `set(P)` et ne contient que des points distincts, P n'a pas de sommet répété. De plus len(hull(P)) = n ≥ 3, et la chaîne monotone renvoie au plus 2 points pour un ensemble aligné (point 1) : S = set(P) n'est donc pas aligné. (Formulation corrigée en session 4 bis : c'est len(hull) ≥ 3, et non n ≥ 3 seul, qui exclut l'alignement.)
3. P est une rotation cyclique de hull(P) : c'est donc la liste des points extrémaux de conv(P), dans le sens direct. La ligne polygonale qui les relie dans cet ordre est ∂conv(P). ∎

**Remarque (indépendance limitée).** La fonction `hull` de `verifier/verify.py` est le même algorithme, presque ligne pour ligne, que celle de `certifier/geometry.py`. Elle est correcte (point 1), mais une erreur d'implémentation serait commune aux deux vérifications.

Dans ce test, `all_left_turns` est redondant (il découle de l'égalité avec l'enveloppe sans points alignés), mais il ne coûte rien. La condition qui manquait en session 3 est l'égalité à l'enveloppe : un pentagramme (sommets d'un pentagone régulier visités dans l'ordre 0, 2, 4, 1, 3) a tous ses virages positifs, mais son enveloppe est le pentagone 0, 1, 2, 3, 4, qui n'en est pas une rotation cyclique ; il est donc rejeté. [VÉRIFIÉ NUMÉRIQUEMENT : contrôle de session 4, `all_left_turns` = vrai et `is_strictly_convex` = faux sur un pentagramme à sommets rationnels.]

Toute la suite utilise la convexité des pièces : l'aire par la formule du lacet (`area`) est une mesure de Lebesgue, `half_planes(Q)` décrit Q comme intersection de demi-plans, Sutherland–Hodgman (`clip`) est correct, et P_i est l'enveloppe de ses sommets.

## 0.1 Les translatés des pièces pavent le plan [DÉMONTRÉ ICI]

**Ce que le code vérifie** (`core.verify`, appelée par `certifier/certify.py` et par `certifier/recompute.py` à partir des JSON) :

- (V1) chaque pièce est strictement convexe et CCW : `is_strictly_convex` (§0.0) ;
- (V2) Σ_i aire(P_i) = |C|, égalité de rationnels ;
- (V3) pour tout (i, j, a, b) avec (j, a, b) ≠ (i, 0, 0) et |a| ≤ amax, |b| ≤ bmax, on a aire(P_i ∩ (P_j + t)) = 0 dès que les boules englobantes se rencontrent. Pour t = 0, seuls les couples j > i sont testés, ce qui suffit par symétrie.

La boule englobante (z_i, r_i) est construite par `core.ball` : z_i est la moyenne des sommets ; r_i est un rationnel dont on vérifie exactement que r_i² ≥ max_v |v − z_i|². Comme P_i est l'enveloppe de ses sommets (lemme 0.0), P_i ⊆ B(z_i, r_i).

Le vérificateur indépendant refait (V1)–(V3) en `Fraction` (étapes E1–E3 de `verifier/verify.py`) ; pour (V3), il prouve la disjonction des intérieurs par une droite d'arête séparatrice (`edge_separates`) pour toutes les translations avec |t| ≤ 2 Rmax.

**Complétude de (V3).** Si P_i et P_j + t ont des intérieurs qui se rencontrent, alors |z_j + t − z_i| ≤ r_i + r_j, donc |t| ≤ ρ := max|z_i − z_j| + 2·max r. C'est `core.radius_bound(balls, 0)` (la racine est majorée puis vérifiée exactement).

Pour t = a·g1 + b·g2, on a |det(g2, t)| = |a|·|det(g2, g1)| = |a|·|C|, d'où |a|·|C| ≤ |t|·|g2| ≤ ρ·|g2|. De même |b|·|C| ≤ ρ·|g1|. `core.translation_bounds` renvoie amax = ⌊ρ|g2|/|C|⌋, le plus grand entier tel que amax²·|C|² ≤ ρ²·|g2|² (test exact), et bmax de même. Hors de ce rectangle d'indices, les boules ne se rencontrent pas. Les couples sautés par le test des boules (`continue` dans `core.verify`) ont aussi des boules disjointes. (V3) vaut donc pour **tous** les (i, j, g) avec (j, g) ≠ (i, 0).

Par ailleurs, `intersection` (`certifier/geometry.py`) renvoie le polygone exact P ∩ (P_j + t) lorsque cette intersection est d'aire > 0 (§ (c).4.7), et une aire calculée nulle lorsqu'elle est d'intérieur vide (lemme 0.1 bis ci-dessous). Son aire est nulle si et seulement si les intérieurs sont disjoints : l'intersection de deux convexes d'intérieurs non disjoints est d'intérieur non vide.

**Lemme 0.1.** Sous (V1)–(V3), la fonction f(x) = Σ_{i, g ∈ G} 1_{P_i + g}(x) vaut 1 presque partout. Autrement dit, les translatés P_i + g recouvrent le plan, et leurs intérieurs sont deux à deux disjoints, à un ensemble de mesure nulle près.

*Preuve.*
1. Les bords ∂(P_i + g) forment une famille dénombrable de segments, donc un ensemble négligeable Z.
2. Hors de Z, par (V3), un point appartient à au plus un intérieur, d'où f ≤ 1 p.p.
3. f est G-périodique. Comme C est un domaine fondamental de G, on a Σ_g mes((X + g) ∩ C) = mes(X) pour tout X mesurable. D'où ∫_C f = Σ_i Σ_g mes((P_i + g) ∩ C) = Σ_i aire(P_i) = |C| par (V2).
4. Donc ∫_C (1 − f) = 0 avec 1 − f ≥ 0 p.p., ce qui donne f = 1 p.p. sur C, puis partout par périodicité.
5. **Recouvrement de tout le plan, frontières comprises.** La famille des translatés P_i + g est localement finie : une
   boule bornée ne rencontre qu'un nombre fini de translatés, car G est un réseau et les P_i sont bornés. Chaque P_i + g
   est fermé. La réunion d'une famille localement finie de fermés est fermée, donc son complément U est ouvert. Par le
   point 4, U est de mesure nulle ; un ouvert de mesure nulle est vide. Les pièces recouvrent donc tout le plan,
   frontières comprises, et la règle « pièce de plus petit indice » définit la couleur de **tout** point. ∎

**Conséquences.**
- La coloration c(x) = couleur de l'unique translaté qui contient x est définie hors de Z. Elle est G-périodique et mesurable. Sur les bords, on fixe la règle du README : x reçoit la couleur de la pièce de plus petit indice i telle que x ∈ P_i + G ; cette règle est G-périodique par construction.
- La preuve n'utilise **que** (V1)–(V3), et non la manière dont les pièces ont été construites (découpage, île étoilée, fusions : `certifier/colourings.py`, `certifier/island.py`). La construction n'a donc pas besoin d'être démontrée.

## 0.2 Réduction de p5 à une somme d'aires [DÉMONTRÉ ICI]

**Définition** [CONNU + H. Gwyn, J. Stavrianos, arXiv:2008.07987v1 (2020), Geombinatorics 32(1) (2022), Th. 2.17–2.22 ; relus en session 3, voir `relecture_preuves.md`, §3(ii)]. Pour une coloration G-périodique dont l'ensemble monochrome S = {(x, θ) : c(x) = c(x + u(θ))} est Jordan-mesurable dans ℝ² × [0, 2π] (ce qui est le cas ici : voir `relecture_preuves.md`, §3(ii), point T2) :

  p(c) = (1/2π) ∫_0^{2π} p(θ) dθ, où p(θ) = |C|⁻¹ · mes{x ∈ C : c(x) = c(x + u(θ))}.

[À VÉRIFIER par un relecteur humain : identification exacte avec la définition de GS. La note `note/v6_45.tex` donne par ailleurs une preuve autonome du lemme 2.10 de GS pour les colorations périodiques boréliennes.]

**Proposition 0.2.** Pour tout θ,

  mes{x ∈ C : c(x) = c(x + u)} = Σ_{(P,Q)} A_PQ(u),

où la somme porte sur toutes les paires P = P_i, Q = P_j + g, g ∈ G, c_i = c_j. Seul un nombre fini de termes est non nul.

*Preuve.*
1. Comme la fonction x ↦ 1[c(x) = c(x + u)] est G-périodique, on peut intégrer sur F au lieu de C : F est un domaine fondamental p.p. par le lemme 0.1 (on prend g = 0 dans la partition).
2. Pour u fixé, hors de l'ensemble nul Z ∪ (Z − u), le point x est dans exactement un P_i et x + u dans exactement un P_j + g. On a alors c(x) = c(x + u) si et seulement si c_i = c_j.
3. Donc 1[c(x) = c(x+u)]·1_F(x) = Σ_{i, j, g : c_i = c_j} 1_{P_i}(x)·1_{P_j + g}(x + u) p.p. On intègre ; la convergence est monotone, sur des termes positifs.
4. Seuls les g avec |g| ≤ diam + 1 contribuent, et ils sont en nombre fini. ∎

**Corollaire** (avec (d)). p5(c) = (1/(π|C|)) ∫_0^π Σ_{(P,Q)} A_PQ(u(θ)) dθ.

Par (a) et (b), on peut restreindre la somme aux paires énumérées par `core.enumerate_pairs`, puis aux paires actives de chaque boîte (`core.active`).

---

## (a) Complétude de l'énumération des translations [DÉMONTRÉ ICI]

**Ce que fait le code.** `core.enumerate_pairs` :
- prend ρ' = 1 + max|z_i − z_j| + 2·max r (`radius_bound(balls, 1)`) ;
- énumère |a| ≤ amax, |b| ≤ bmax, donnés par `translation_bounds(cfg, ρ')`. Les journaux de la session 2 donnaient amax = bmax = 2 pour les deux colorations ; `enumerate_pairs` imprime ces valeurs ;
- élimine les (i, j, t) tels que |z_j + t − z_i| > 1 + r_i + r_j.

**Lemme a.1** (ce que le code utilise). Si A_PQ(u) > 0 pour un |u| = 1, avec Q = P_j + t, alors |z_j + t − z_i| ≤ 1 + r_i + r_j. En particulier |t| ≤ ρ', et donc |a| ≤ amax et |b| ≤ bmax.

*Preuve.*
1. A_PQ(u) > 0 fournit x ∈ P avec x + u ∈ Q. Alors |z_j + t − z_i| ≤ |z_j + t − (x + u)| + |u| + |x − z_i| ≤ r_j + 1 + r_i.
2. On en tire |t| ≤ |z_i − z_j| + 1 + r_i + r_j ≤ ρ'.
3. La conclusion vient de l'argument de projection du §0.1 : |a|·|C| = |det(g2, t)| ≤ |t|·|g2|. ∎

L'énumération du code est donc complète, et le test des boules n'élimine que des triplets sans couple de points à distance 1.

**Théorème a.2** (résultat le plus fort ; calcul exact). Pour DISQP32 comme pour ILEP256, s'il existe x ∈ P_i et y ∈ P_j + a·g1 + b·g2 avec |x − y| ≤ 1, alors |a| ≤ 1 et |b| ≤ 1, quelles que soient les couleurs de P_i et P_j. Pour des pièces de **même couleur** à distance < 1, on a de plus (a, b) ∈ {(0,0), (±1,0), (0,±1), (1,−1), (−1,1)} : (±1, ±1) de même signe est exclu.

*Preuve, partie 1 : projection.*
1. Soient x ∈ P_i ⊆ F et y = y' + t avec y' ∈ P_j ⊆ F, |x − y| ≤ 1 et t = a·g1 + b·g2.
2. Comme y = y' + t, on a t = (y − x) − (y' − x), donc, par linéarité de det(g2, ·),

   **det(g2, t) = det(g2, y − x) − det(g2, y' − x)**,

   avec det(g2, t) = a·det(g2, g1). Comme |det(g2, y − x)| ≤ |g2|·|y − x| ≤ |g2| et |det(g2, y' − x)| ≤ W2, où W2 := max_F det(g2, ·) − min_F det(g2, ·) (car x, y' ∈ F), on obtient |a|·|C| ≤ W2 + |g2|.
   *Correction (session 4) : la session 3 écrivait une somme det(g2, y' − x) + det(g2, y − x) ; c'est une différence puisque t = (y − x) − (y' − x), et la majoration en valeur absolue est inchangée.* [VÉRIFIÉ NUMÉRIQUEMENT : contrôle de session 4, 1000 tirages rationnels exacts, la différence est juste 1000/1000 et la somme fausse 1000/1000.]
3. Ce max et ce min sont atteints en des sommets, car det(g2, ·) est linéaire. W2/|g2| est la largeur de F orthogonalement à g2.
4. De même, |b|·|C| ≤ W1 + |g1|.
5. `verifier/verify.py` (étape E4) calcule exactement W1, W2 sur les sommets de toutes les pièces, puis, par `smallest_k`, le plus petit k ≥ 1 tel que k|C| − W2 > 0 et (k|C| − W2)² > |g2|² (et de même pour W1, g1). Il trouve k = 2 dans les deux cas et pour les deux colorations. Comme |a|·|C| − W2 ≤ |g2|·|x − y|, la condition donne |x − y| > 1 dès que |a| ≥ 2 ; la condition est monotone en k. [VÉRIFIÉ NUMÉRIQUEMENT, calcul exact en rationnels ; marges (2|C| − W)² − |g|² : 3,9024 et 3,9024 (DISQP32), 3,8850 et 3,8141 (ILEP256), valeurs de la relecture de session 3, imprimées par E4.]

Valeurs (calcul exact de la session 3 ; les rationnels exacts sont recalculés par E4) :

| | \|C\| | \|g1\| ≈ \|g2\| | \|C\|/\|g2\| (composante ⊥ par unité de a) | diam max d'une pièce | diam F | W2/\|g2\| | W1/\|g1\| | 2\|C\| − W2 vs \|g2\| | 2\|C\| − W1 vs \|g1\| |
|---|---|---|---|---|---|---|---|---|---|
| DISQP32 | 3,343490983 | 1,964874255 | 1,70163102 | 1,13442068 (d² = 321727569802710534385441/2,5·10²³) | 2,83605170 | 1,98523619 | 1,98523619 | 2,78624 > 1,96487 | 2,78624 > 1,96487 |
| ILEP256 | 3,331299049 | 1,961288557 | 1,69852571 | 0,93711659 (d² = 87818750622363186460141/10²³) | 2,82976132 | 1,97931354 | 1,98583281 | 2,78059 > 1,96129 | 2,76781 > 1,96129 |

Le seuil plus grossier, par le seul diamètre (|t| ≤ diam F + 1, donc |a|·|C|/|g2| ≤ diam F + 1), donne déjà |a| ≥ 3 ou |b| ≥ 3 impossible, puisque 3 × 1,70 = 5,10 > 3,84. Cela justifie directement l'énumération du code (|a|, |b| ≤ 2). (Ce seuil grossier n'est pas recalculé par le dépôt ; il n'est pas nécessaire.)

*Preuve, partie 2 : calcul exact pour |a|, |b| ≤ 1.*
1. Pour les 9 translations et les couples (i, j), on calcule dist(P_i, P_j + t)² exactement (`verifier/verify.py`, étape E5, fonction `dist2`, pour les couples de même couleur).
2. Pré-filtre exact : si l'écart des boîtes englobantes rationnelles est ≥ 1, alors dist ≥ 1.
3. Sinon, `strictly_separated` cherche une droite d'arête (de P ou de Q) qui sépare strictement les deux polygones. Pour deux polygones convexes compacts, ces polygones sont disjoints si et seulement si une telle droite existe (`relecture_preuves.md`, T7) ; sinon dist = 0. Si les polygones sont disjoints, dist² = min des distances sommet–arête, dans les deux sens, car pour deux convexes disjoints un couple de points les plus proches contient un sommet.

Résultats exacts :
- **Toutes couleurs** : les 9 translations ont un couple à distance < 1. Pour (±1, ±1) de même signe, la distance minimale vaut d² ≈ 0,3217 (DISQP32) et 0,3218 (ILEP256). [VÉRIFIÉ NUMÉRIQUEMENT en session 3, calcul exact ; ce calcul toutes couleurs n'a pas d'équivalent dans le dépôt et n'est pas nécessaire.]
- **Même couleur** : (±1, ±1) de même signe n'a aucun couple à distance < 1, et les 7 autres en ont. Pour DISQP32, la distance minimale au carré vaut 0,9652 pour les 6 translations non nulles. Pour ILEP256, elle vaut 0,7097 pour (±1, 0) et (±1, ∓1), et 0,9514 pour (0, ±1). [VÉRIFIÉ NUMÉRIQUEMENT en session 3 ; ces minima ne sont pas imprimés par `verifier/verify.py`.]
- **Recoupement.** Le nombre de paires de même couleur avec dist² < 1 < max² est de **394** (DISQP32) et **1804** (ILEP256). Ce sont exactement les nombres de `core.enumerate_pairs`, obtenus ici par un code distinct (`verifier/verify.py`, étape E5) sur un domaine d'indices prouvé complet. ∎

**Remarque.** Le théorème a.2 rend le pré-filtre par boules et la borne amax = 2 du code superflus. Ils sont corrects (lemme a.1), simplement prudents.

---

## (b) Correction des filtres de paires [DÉMONTRÉ ICI]

Deux filtres éliminent des paires. Le premier agit une fois pour toutes (`core.enumerate_pairs`, test `d2 < 1 < m2`), le second boîte par boîte (`core.active`, appelé dans `core.box_bound`).

### b.1 Le support de A_PQ

**Lemme b.1.** Si A_PQ(u) > 0, alors u ∈ int M, où M = Q − P.

*Preuve.* Si aire(P ∩ (Q − u)) > 0, ce convexe contient une boule B(x, ε). On a alors x ∈ P et x + u + w ∈ Q pour |w| < ε. Donc u + w = (x + u + w) − x ∈ Q − P, et B(u, ε) ⊆ M. ∎

La réciproque (u ∈ int M ⇒ A > 0) est vraie aussi, mais elle ne sert pas : seul le sens « éliminé ⇒ nul » est nécessaire.

### b.2 Filtre global d2 < 1 < m2

**Code.**
- `d2 = dist2_origin_polygon(M)` (`certifier/geometry.py`). Le résultat vaut 0 si cross(M_k, M_{k+1}, 0) ≥ 0 pour toutes les arêtes (variable `inside`), c'est-à-dire si 0 ∈ M fermé (M est CCW, sortie de `hull`). Sinon, c'est le minimum exact des distances au carré de 0 aux segments-arêtes, et donc dist(0, M)², puisque 0 est hors du convexe M.
- `m2 = max2_origin_polygon(M)` = max |sommet|².
- La paire est **gardée si et seulement si d2 < 1 < m2** (`core.enumerate_pairs`).

**Proposition b.2.** Si d2 ≥ 1 ou m2 ≤ 1, alors A_PQ(u) = 0 pour tout |u| = 1.

*Preuve.* Par le lemme b.1, il suffit de montrer que le cercle unité ne rencontre pas int M.
- **Cas d2 ≥ 1.** Si u ∈ int M avec |u| = 1, une boule B(u, ε) ⊆ M contient le point (1 − ε/2)u, de norme < 1. Alors dist(0, M) < 1, ce qui est contradictoire.
- **Cas m2 ≤ 1.** M, enveloppe de ses sommets, est contenu dans le disque fermé unité D. Donc int M ⊆ int D = disque ouvert, qui ne rencontre pas le cercle. ∎

Le pré-filtre par boules est justifié par le lemme a.1.

### b.3 Filtre angulaire par boîte

**Code** (`core.enumerate_pairs` et `core.active`).
- **Branche `if d2 == 0`** (0 ∈ M) : `pr.always = True`, `pr.span = None` ; la paire n'est jamais éliminée.
- **Branche `else`** (d2 ≠ 0) : `pr.always = False`, et on calcule :
  - ref = moyenne des sommets de M ;
  - pour chaque sommet v, α_v = `angle_arb(v, ref)` = atan2(cross(ref, v), ⟨ref, v⟩), en boule Arb ;
  - φ = atan2(ref_y, ref_x), en boule Arb ;
  - lo_q = min_v `fmpq_lower`(α_v) et hi_q = max_v `fmpq_upper`(α_v), qui sont des rationnels ;
  - a0 = `fmpq_lower`((φ + lo_q)/π) et a1 = `fmpq_upper`((φ + hi_q)/π), avec π = `arb.pi()`. On pose `pr.span` = [a0, a1].
- **Test** : `active(pr, x0, x1)` renvoie vrai si `pr.always` est vrai ; sinon, il est faux si et seulement si, pour chaque k ∈ {−4, −2, 0, 2, 4}, on a x1 < a0 + k ou x0 > a1 + k. Les comparaisons sont exactes, entre rationnels. Autrement dit, [x0, x1] ne rencontre aucun [a0 + k, a1 + k].

**Lemme b.3 (secteur).** Supposons 0 ∉ M et ref ∈ M \ {0}. Pour w ∈ M, notons α(w) ∈ (−π, π) la valeur principale de l'angle orienté de ref à w, c'est-à-dire atan2(cross(ref, w), ⟨ref, w⟩). Alors α(w) ∈ [min_v α_v, max_v α_v].

*Preuve.*
1. M est compact convexe et 0 ∉ M. Il existe donc un vecteur unitaire n tel que ⟨n, w⟩ > 0 sur M (séparation stricte).
2. Sur le demi-plan ouvert H = {⟨n, ·⟩ > 0}, notons β(w) ∈ (−π/2, π/2) l'angle orienté de n à w. La fonction tan β(w) = ⟨n⊥, w⟩/⟨n, w⟩ est quasi-linéaire. Pour tout c, {w ∈ H : ⟨n⊥, w⟩ ≤ c⟨n, w⟩} et {≥} sont des demi-plans intersectés avec H.
3. Si w = Σλ_k v_k est une combinaison convexe des sommets et c = max_k tan β(v_k), alors ⟨n⊥, w⟩ − c⟨n, w⟩ = Σλ_k(⟨n⊥, v_k⟩ − c⟨n, v_k⟩) ≤ 0. Donc β(w) ≤ max β(v_k), et de même β(w) ≥ min β(v_k).
4. Pour w ∈ H, l'angle de ref à w vaut β(w) − β(ref) modulo 2π, et |β(w) − β(ref)| < π. C'est donc la valeur principale : α(w) = β(w) − β(ref). La translation par −β(ref) conserve l'encadrement. ∎

ref, moyenne des sommets, appartient à M par convexité, et ref ≠ 0 dès que 0 ∉ M.

**Proposition b.3.** Si `active(pr, x0, x1)` est faux, alors A_PQ(u(θ)) = 0 pour tout θ ∈ [x0π, x1π].

*Preuve.*
1. **La paire est dans la branche d2 > 0.** Comme `active` renvoie vrai dès que `pr.always` est vrai, l'hypothèse « `active` faux » donne `pr.always` faux. Or `enumerate_pairs` ne pose `pr.always = False` que dans la branche `else` du test `if d2 == 0`. Donc d2 ≠ 0, et d2 > 0 puisque d2 est un carré de distance. Dans cette branche, `dist2_origin_polygon(M)` n'a pas renvoyé 0 : le test `inside` a échoué, il existe donc une arête de M avec cross(M_k, M_{k+1}, 0) < 0. L'origine est alors strictement du côté extérieur de la droite d'une arête du polygone convexe CCW M, d'où 0 ∉ M. `pr.span = [a0, a1]` est défini comme ci-dessus, et le lemme b.3 s'applique.
   *Correction (session 4) : la session 3 écrivait « u ∈ M, donc d2 > 0 ». C'est faux comme déduction (un convexe peut contenir u et 0) : la positivité de d2, donc 0 ∉ M, vient de la branche `else` de `if d2 == 0` où se trouve la paire, et u ∈ M ne sert qu'à appliquer le lemme b.3.*
2. Supposons, par l'absurde, A_PQ(u(θ)) > 0 pour un θ ∈ [x0π, x1π] ⊆ [0, π]. Par le lemme b.1, u = u(θ) ∈ int M ⊆ M.
3. L'argument de u est φ + α(u) modulo 2π, d'où θ = φ + α(u) + 2πk pour un entier k.
4. **Encadrements.** Les boules Arb contiennent les vraies valeurs (sémantique d'Arb). Donc lo_q ≤ min α_v ≤ α(u) ≤ max α_v ≤ hi_q (lemme b.3), puis a0 ≤ (φ + lo_q)/π ≤ (φ + α(u))/π ≤ (φ + hi_q)/π ≤ a1. Ainsi θ/π ∈ [a0 + 2k, a1 + 2k].
5. **Valeurs de k.** φ ∈ (−π, π] et α ∈ (−π, π), donc (φ + α)/π ∈ (−2, 2). Avec θ/π ∈ [0, 1], on obtient 2k ∈ (−2, 3), soit 2k ∈ {0, 2} ⊆ {−4, …, 4}.
6. Alors [x0, x1] rencontre [a0 + 2k, a1 + 2k], et `active` est vrai : contradiction. ∎

Les boîtes sont des intervalles fermés et le test l'est aussi. Le choix des boîtes est flottant, mais il n'intervient pas.

**Conséquence.** Pour chaque boîte, ∫_I Σ_{toutes paires} A_PQ(u(θ)) dθ = ∫_I Σ_{paires actives} A_PQ(u(θ)) dθ, exactement.

**Hypothèse utilisée** [CONNU + documentation FLINT/Arb, « inclusion principle » du module arb.h] : les fonctions `arb.atan2`, `arb.pi`, les opérations arithmétiques et `arb(fmpq)` de python-flint 0.9.0 / Arb renvoient des boules qui contiennent la valeur exacte. `fmpq_lower` et `fmpq_upper` (`certifier/geometry.py`) lisent `lower()` et `upper()`, qui sont des nombres dyadiques exacts. Les conversions sont donc exactes.

---

## (c) Lemme A ≤ T² et majoration d'une boîte [DÉMONTRÉ ICI]

Soient P, Q des polygones convexes compacts d'intérieur non vide, A(u) = aire(P ∩ (Q − u)) et I(u) = P ∩ (Q − u).

### c.1 Continuité et support

On a |A(u) − A(v)| ≤ aire((Q − u) Δ (Q − v)) ≤ per(Q)·|u − v|. A est donc lipschitzienne (voir aussi la proposition c.4.3). L'ensemble S := {u : A(u) > 0} est ouvert, et S ⊆ int M par le lemme b.1.

### c.2 Concavité de √A sur S (Brunn–Minkowski)

**Lemme c.2.** S est convexe, et g := √A est concave sur S.

*Preuve.*
1. Soient u1, u2 ∈ S, λ ∈ [0, 1] et u_λ = λu1 + (1 − λ)u2. Si x_k ∈ I(u_k), c'est-à-dire x_k ∈ P et x_k + u_k ∈ Q, alors x_λ = λx1 + (1 − λ)x2 ∈ P et x_λ + u_λ = λ(x1 + u1) + (1 − λ)(x2 + u2) ∈ Q, par convexité de P et de Q.
2. Donc λ·I(u1) + (1 − λ)·I(u2) ⊆ I(u_λ).
3. Brunn–Minkowski dans ℝ² [CONNU + R. J. Gardner, *The Brunn–Minkowski inequality*, Bull. Amer. Math. Soc. 39 (2002) 355–405], pour des compacts non vides, donne aire(λK + (1−λ)L)^{1/2} ≥ λ·aire(K)^{1/2} + (1 − λ)·aire(L)^{1/2}. D'où g(u_λ) ≥ λg(u1) + (1 − λ)g(u2) > 0.
4. Donc u_λ ∈ S et g est concave. ∎

**Fermeture.** On n'a besoin ni de la fermeture de S ni de l'égalité S = int M. La majoration ci-dessous traite séparément u ∈ S et u ∉ S. Hors de S, A = 0 par définition de S, sans aucun argument de passage à la limite.

### c.3 Le majorant T²

**Proposition c.3.** Soit u0 ∈ S (A0 = A(u0) > 0) tel que A soit différentiable en u0, de gradient G. On pose

  T(u) = √A0 + ⟨G, u − u0⟩/(2√A0).

Alors, pour **tout** u ∈ ℝ²,

  A(u) ≤ T(u)² = A0 + ⟨G, d⟩ + ⟨G, d⟩²/(4A0), avec d = u − u0.

*Preuve.*
1. g = √A est différentiable en u0, de gradient G/(2√A0), puisque A0 > 0.
2. **Cas u ∈ S.** φ(t) = g(u0 + t(u − u0)) est concave sur [0, 1], car S est convexe, et dérivable en 0. Donc φ(1) ≤ φ(0) + φ'(0), c'est-à-dire g(u) ≤ T(u). Comme 0 ≤ g(u) ≤ T(u), on obtient A(u) = g(u)² ≤ T(u)².
3. **Cas u ∉ S.** A(u) = 0 ≤ T(u)². ∎

**Cas A0 = 0.** Le code n'emploie jamais (M1) dans ce cas : `use_m2 = (A0 == 0)` dans `core.box_bound`, et le cas est traité par (M2) (c.6).

**Cas non différentiable.** Le code **n'emploie pas** de sur-gradient. Dans `core.box_bound`, la boucle `while True` déplace u0 jusqu'à ce que `is_regular(pr.par, u0)` soit vrai pour **toutes** les paires actives ; par le théorème c.4.5, A est alors différentiable en u0 pour chacune. Le nombre de déplacements est compté (`stats["u0_attempts"]`) et `certifier/certify.py` imprime le nombre de boîtes où il est > 0 ; les journaux de la session 2 donnaient 0. La validité ne dépend pas de ce nombre.

### c.4 Formule du gradient et différentiabilité [DÉMONTRÉ ICI]

On suppose désormais P et Q strictement convexes et CCW (lemme 0.0 ; Q = P_j + t l'est aussi). On fixe u0 et on pose K := Q − u0. Pour une arête f0 de Q, on note f = f0 − u0 l'arête correspondante de K, ν_f sa normale sortante unitaire (la même pour f0 et f), et

  ℓ_f(u) := longueur((f0 − u) ∩ P), de sorte que ℓ_f(u0) = |f ∩ P|.

On veut démontrer : **si aucune arête de P n'est colinéaire (même droite) à une arête de Q − u0, alors A est différentiable en u0 et**

  **∇A(u0) = Γ(u0) := −Σ_{f arête de Q − u0} ν_f · |f ∩ P|.**

La preuve est élémentaire : on établit une formule **exacte** pour l'accroissement A(u0 + h) − A(u0) (c.4.1–c.4.3), puis on passe à la limite grâce à la continuité des ℓ_f (c.4.4–c.4.5).

**Lemme c.4.1 (comptage des traversées).** Soit K un polygone convexe compact d'intérieur non vide, d'arêtes f et de normales sortantes unitaires ν_f, et soit h ∈ ℝ² \ {0}. Pour chaque arête f, posons Π_f(h) := {y − τh : y ∈ f, τ ∈ [0, 1]} et σ_f := signe de ⟨h, ν_f⟩ ∈ {−1, 0, 1}. Alors, pour presque tout z ∈ ℝ²,

  1_K(z + h) − 1_K(z) = −Σ_f σ_f · 1_{Π_f(h)}(z).

*Preuve.*
1. **Ensemble exclu.** Soit N la réunion de ∂K, de ∂K − h et des droites parallèles à h passant par un sommet de K. C'est une réunion finie de segments et de droites, donc un ensemble négligeable. Soit z ∉ N et D = {z + τh : τ ∈ ℝ}.
2. Remarquons que z ∈ Π_f(h) si et seulement si le segment [z, z + h] rencontre f (y = z + τh ∈ f avec τ ∈ [0, 1]).
3. **Si D ne rencontre pas int K.** Alors D ∩ K est vide, ou réduit à une face de K contenue dans une droite d'appui. Une telle face contient un sommet de K, ce qui est exclu puisque D ne passe par aucun sommet. Donc D ∩ K = ∅ : les deux membres sont nuls (le segment [z, z + h] ⊆ D ne rencontre aucune arête).
4. **Si D rencontre int K.** Alors D ∩ K = {z + τh : τ ∈ [τ_e, τ_s]} avec τ_e < τ_s, et D ∩ ∂K = {z + τ_e h, z + τ_s h}. Ces deux points ne sont pas des sommets ; chacun est intérieur à une seule arête, notée f_e (entrée) et f_s (sortie). Aucune de ces deux arêtes n'est parallèle à h (sinon D la contiendrait, avec ses sommets). Comme z + τh ∈ int K pour τ légèrement supérieur à τ_e et K ⊆ {x : ⟨ν_{f_e}, x − (z + τ_e h)⟩ ≤ 0}, on a ⟨h, ν_{f_e}⟩ < 0, donc σ_{f_e} = −1 ; de même σ_{f_s} = +1.
5. Comme z, z + h ∉ ∂K, on a τ_e, τ_s ∉ {0, 1}, et 1_K(z) = [τ_e < 0 < τ_s], 1_K(z + h) = [τ_e < 1 < τ_s]. On vérifie sur les six positions relatives de τ_e < τ_s par rapport à 0 < 1 que

   [τ_e < 1 < τ_s] − [τ_e < 0 < τ_s] = [0 < τ_e < 1] − [0 < τ_s < 1].

   Par le point 2, [0 < τ_e < 1] = 1_{Π_{f_e}(h)}(z) et [0 < τ_s < 1] = 1_{Π_{f_s}(h)}(z). Pour toute autre arête f, z ∉ Π_f(h), puisque [z, z + h] ne rencontre ∂K qu'en des points de f_e ou de f_s intérieurs à ces arêtes. Le membre de droite vaut donc −σ_{f_e}·[0 < τ_e < 1] − σ_{f_s}·[0 < τ_s < 1], ce qui est la formule. ∎

**Lemme c.4.2 (parallélogramme coupé par P).** Avec les notations précédentes et un compact convexe P,

  aire(P ∩ Π_f(h)) = |⟨h, ν_f⟩| · ∫_0^1 λ_f(τ) dτ, où λ_f(τ) := longueur((f − τh) ∩ P).

*Preuve.* Si ⟨h, ν_f⟩ = 0, Π_f(h) est contenu dans une droite et les deux membres sont nuls. Sinon, écrivons f = {a + σê : σ ∈ [0, |f|]}, avec ê unitaire ; le polygone étant CCW, ν_f = (ê_y, −ê_x). L'application affine Φ(σ, τ) = a + σê − τh envoie [0, |f|] × [0, 1] sur Π_f(h), et son jacobien vaut det(ê, −h) = ê_y h_x − ê_x h_y = ⟨ν_f, h⟩ ≠ 0 ; elle est donc injective. Par changement de variables puis Fubini–Tonelli,

  aire(P ∩ Π_f(h)) = |⟨h, ν_f⟩| ∫_0^1 ∫_0^{|f|} 1_P(a + σê − τh) dσ dτ = |⟨h, ν_f⟩| ∫_0^1 λ_f(τ) dτ. ∎

**Proposition c.4.3 (accroissement exact).** Pour tous u0 et h,

  A(u0 + h) − A(u0) = −Σ_{f0 arête de Q} ⟨h, ν_f⟩ ∫_0^1 ℓ_f(u0 + τh) dτ.

*Preuve.* Comme z ∈ Q − u0 − h ⇔ z + h ∈ K, on a A(u0 + h) = ∫_P 1_K(z + h) dz et A(u0) = ∫_P 1_K(z) dz. On intègre le lemme c.4.1 sur P :

  A(u0 + h) − A(u0) = −Σ_f σ_f · aire(P ∩ Π_f(h)) = −Σ_f σ_f |⟨h, ν_f⟩| ∫_0^1 λ_f(τ) dτ

par le lemme c.4.2. On conclut avec σ_f |⟨h, ν_f⟩| = ⟨h, ν_f⟩ et λ_f(τ) = longueur((f0 − u0 − τh) ∩ P) = ℓ_f(u0 + τh). ∎

En particulier |A(u0 + h) − A(u0)| ≤ |h| Σ_f |f| = per(Q)·|h|, ce qui redonne c.1.

**Lemme c.4.4 (continuité de ℓ_f).** Si aucune arête de P n'est portée par la droite de f0 − u0, alors ℓ_f est continue en u0.

*Preuve.* Écrivons f0 = {a + σê : σ ∈ [0, |f0|]}, avec ê unitaire, et P = ∩_e {x : ⟨ν_e, x⟩ ≤ c_e}, l'intersection portant sur les arêtes e de P (lemme 0.0). Le point a − u + σê est dans P si et seulement si, pour chaque arête e de P,

  σ⟨ν_e, ê⟩ ≤ c_e − ⟨ν_e, a − u⟩ =: δ_e(u),

où δ_e est une fonction affine, donc continue, de u.
- **Arêtes e non parallèles à f0** (⟨ν_e, ê⟩ ≠ 0) : la contrainte s'écrit σ ≤ δ_e(u)/⟨ν_e, ê⟩ ou σ ≥ δ_e(u)/⟨ν_e, ê⟩ selon le signe de ⟨ν_e, ê⟩. Ce sont des bornes continues en u.
- **Arêtes e parallèles à f0** (⟨ν_e, ê⟩ = 0, normales égales ou opposées) : la contrainte ne dépend pas de σ ; elle s'écrit δ_e(u) ≥ 0. La droite de f0 − u0 est {⟨ν_e, x⟩ = ⟨ν_e, a − u0⟩} et celle de e est {⟨ν_e, x⟩ = c_e}. Par hypothèse elles sont distinctes, donc δ_e(u0) ≠ 0, et le signe de δ_e est constant au voisinage de u0.

S'il existe une arête parallèle e avec δ_e(u0) < 0, alors ℓ_f = 0 au voisinage de u0. Sinon, toutes les contraintes parallèles sont satisfaites au voisinage de u0 et peuvent être oubliées ; alors {σ ∈ [0, |f0|] : a − u + σê ∈ P} = [α(u), β(u)] (vide si α(u) > β(u)), où α(u) est le maximum de 0 et des bornes inférieures, et β(u) le minimum de |f0| et des bornes supérieures. α et β sont continues en u0, donc ℓ_f(u) = max(0, β(u) − α(u)) l'est aussi. ∎

**Théorème c.4.5 (gradient).** Disons que u0 est **régulier** si aucune arête de P n'est portée par la même droite qu'une arête de Q − u0. Si u0 est régulier, A est différentiable en u0 et

  ∇A(u0) = Γ(u0) = −Σ_{f arête de Q − u0} ν_f · |f ∩ P|.

*Preuve.* Par la proposition c.4.3, pour tout h,

  A(u0 + h) − A(u0) − ⟨Γ(u0), h⟩ = −Σ_f ⟨h, ν_f⟩ ∫_0^1 (ℓ_f(u0 + τh) − ℓ_f(u0)) dτ,

donc |A(u0 + h) − A(u0) − ⟨Γ(u0), h⟩| ≤ |h| · Σ_f sup_{|v − u0| ≤ |h|} |ℓ_f(v) − ℓ_f(u0)|. Par le lemme c.4.4, appliqué à chaque arête (régularité), la somme tend vers 0 avec h. ∎

*Remarques.*
- La régularité est suffisante, non nécessaire : deux arêtes colinéaires mais disjointes n'empêchent pas la différentiabilité. Le test codé est donc prudent ; cela n'a pas de conséquence.
- L'ensemble des points non réguliers est une réunion finie de droites ; le théorème montre que A est différentiable sur son complémentaire ouvert, de gradient Γ continu (lemme c.4.4).
- La rédaction de la session 3 obtenait la même formule par un argument distributionnel (Gauss–Green pour 1_Q, convolution et régularisation). La preuve ci-dessus est directe et donne de plus une identité exacte pour l'accroissement. [VÉRIFIÉ NUMÉRIQUEMENT : contrôle de session 4 sur un couple de polygones aléatoires et un grand accroissement h, les deux membres de c.4.3 coïncident à 10⁻⁸ près, l'erreur de la quadrature utilisée.]

**c.4.6 Le test codé de la régularité.**
- `parallel_edges(P, Q)` (`certifier/geometry.py`) liste les couples d'arêtes (e de P, f0 de Q) de droites parallèles (test exact a·b2 − b·a2 = 0, ce qui inclut les normales opposées), normalisées en a·x + b·y = c_P et a·x + b·y = c_Q, avec c_Q = c2/k et k = a2/a ou b2/b, y compris k < 0.
- `is_regular(par, u)` renvoie faux si et seulement si c_Q − (a·u_x + b·u_y) = c_P pour l'un d'eux. C'est exactement la coïncidence de la droite de f0 − u avec celle de e : la droite de f0 − u est a·x + b·y = c_Q − (a·u_x + b·u_y).
- Deux droites non parallèles ne coïncident jamais. Donc `is_regular` vrai ⇔ u régulier au sens du théorème c.4.5 (la condition est exactement celle du théorème).
- Dans `core.box_bound`, le test porte sur `pr.par = parallel_edges(P, Q)` avec Q = P_j + t : la translation t est incluse, et u0 joue le rôle de u.

**c.4.7 Ce que calcule `area_and_gradient` : lien avec l'étiquetage de Sutherland–Hodgman.** Soit u0 régulier avec A0 > 0.

*Le code.* `area_and_gradient(P, Q, u0)` forme `Qu = translate(Q, −u0)` = Q − u0, puis `(S, T) = intersection(P, Qu)`. `intersection` part de S = P avec toutes les étiquettes égales à 0 (« arête portée par ∂P »), puis découpe successivement S par chacun des demi-plans (a, b, c) de `half_planes(Qu)` (normale sortante non unitaire (a, b), Q − u0 = ∩ {a·x + b·y ≤ c}) au moyen de `clip(S, T, a, b, c, 1)`. Dans `clip`, pour chaque arête p → q de l'entrée, avec dp = a·p_x + b·p_y − c et dq de même :
- si dp ≤ 0 : on émet p avec l'étiquette de l'arête p → q ; si de plus dq > 0, on émet le point de sortie avec l'étiquette **1** (l'arête qui en part est portée par la droite de coupe) ;
- si dp > 0 et dq ≤ 0 : on émet le point d'entrée avec l'étiquette de p → q (l'arête qui en part est un sous-segment de p → q) ;
- si dp > 0 et dq > 0 : rien.

Si S a moins de 3 sommets, la fonction renvoie (0, (0, 0)) ; sinon elle renvoie A = `area(S)` et

  G = Σ_{i : T[i] = 0} (y_{i+1} − y_i, −(x_{i+1} − x_i)),

c'est-à-dire la somme, sur les arêtes de S d'étiquette 0, de n_e = |e|·ν_e.

**Lemme c.4.7.** Sous ces hypothèses, G = Γ(u0) = ∇A(u0).

*Preuve.*
1. **Sutherland–Hodgman** [DÉMONTRÉ ICI, dans `relecture_preuves.md`, §3(iii), lemme SH]. Si l'entrée parcourt dans le sens direct le bord d'un polygone convexe d'aire > 0 (sommets répétés et alignés admis) et si l'intersection avec le demi-plan est d'aire > 0, la sortie de `clip` parcourt le bord de l'intersection dans le sens direct, une seule fois, sans retour en arrière. Chaque arête de longueur > 0 de la sortie est soit un sous-segment d'une arête d'entrée, avec la même étiquette, soit la corde portée par la droite de coupe, avec l'étiquette 1. Une arête d'entrée portée par la droite de coupe (dp = dq = 0) est recopiée avec son ancienne étiquette.
2. **Récurrence.** I := I(u0) est contenu dans chaque polygone intermédiaire, qui est donc d'aire ≥ A0 > 0 ; le lemme SH s'applique à chaque étape, en partant de P, strictement convexe CCW (lemme 0.0). La sortie finale S parcourt ∂I dans le sens direct, une seule fois. Par récurrence, chaque arête de S de longueur > 0 est :
   - d'étiquette 0 : contenue dans une arête de P, donc **portée par ∂P** ;
   - d'étiquette 1 : contenue dans la droite L_f d'une arête f de Q − u0, et même dans I ∩ L_f ⊆ (Q − u0) ∩ L_f = f, donc **portée par ∂(Q − u0)**.
3. **Les arêtes de S sur L_f.** L_f est une droite d'appui de Q − u0 ⊇ I, donc I ∩ L_f ⊆ ∂I et I ∩ L_f = P ∩ (Q − u0) ∩ L_f = P ∩ f. Comme S parcourt ∂I une seule fois, la somme des longueurs des arêtes de S de longueur > 0 contenues dans L_f vaut longueur(I ∩ L_f) = |f ∩ P| = ℓ_f(u0). Chacune de ces arêtes est d'étiquette 1 et provient de f :
   - une arête d'étiquette 0 de longueur > 0 dans L_f serait un sous-segment d'une arête de P porté par L_f : c'est exactement ce que la **régularité** exclut ;
   - une arête d'étiquette 1 provenant d'une autre arête f' serait contenue dans L_{f'} ∩ L_f, qui est au plus un point, puisque Q − u0 est strictement convexe et que ses arêtes ont des droites distinctes.
   Réciproquement, toute arête d'étiquette 1 de longueur > 0 est contenue dans un L_f (point 2). Les arêtes d'étiquette 1 sont donc exactement les arêtes de S de longueur > 0 portées par les L_f, groupées par f.
4. **Orientation.** Pour une arête e de S portée par L_f, I est à gauche de e (parcours direct) et I ⊆ {⟨ν_f, ·⟩ ≤ c_f} : la normale sortante de e est ν_f, et (dy, −dx) = |e|·ν_f.
5. **Télescopage.** Σ_{toutes les arêtes de S} (dy, −dx) = (0, 0), puisque S est fermé ; les arêtes de longueur nulle (points dupliqués des cas limites dp = 0 ou dq = 0) contribuent (0, 0). Donc
   G = Σ_{étiquette 0} (dy, −dx) = −Σ_{étiquette 1} (dy, −dx) = −Σ_f ν_f · ℓ_f(u0) = Γ(u0),
   et Γ(u0) = ∇A(u0) par le théorème c.4.5. ∎

Autrement dit, le gradient est lu sur les arêtes de P ∩ (Q − u0) portées par ∂P (étiquette 0) : c'est l'opposé de la somme des normales pondérées par les longueurs sur la partie du bord portée par ∂(Q − u0) (étiquette 1), et c'est cette dernière somme qui apparaît dans la formule ∇A(u0) = −Σ_f ν_f |f ∩ P|. Aucun facteur de normalisation n'intervient : (dy, −dx) est de norme |e|. [VÉRIFIÉ NUMÉRIQUEMENT : la relecture de session 3 a comparé exactement G à Γ(u0), calculé par découpage de Cyrus–Beck indépendant, sur 400 + 400 cas tirés dans les paires réelles, avec égalité 800/800 ; un contrôle de session 4 sur 294 couples de polygones rationnels aléatoires, avec `area_and_gradient` du dépôt, donne l'égalité exacte 294/294 et des étiquettes cohérentes avec le point 2 dans 294/294 cas. Ces scripts de contrôle ne sont pas distribués.]

### c.5 La majoration (M1) d'une boîte telle que codée

Dans `core.box_bound` :
1. On choisit u0 rationnel (`rational(..., 2**40)`, dénominateur 2⁴⁰), régulier pour toutes les paires actives (boucle `while True` sur `is_regular`). Le choix est flottant mais quelconque.
2. Pour chaque paire active, (A0, G) = `area_and_gradient(pr.P, pr.Q, u0)`, exact. Si A0 > 0 et si (M1) est retenue, on agrège S0 += A0, (SGx, SGy) += G et (Mxx, Mxy, Myy) += G·Gᵀ/(4A0), exactement en fmpq.
3. Par c.3 et le lemme c.4.7, pour θ ∈ I et d(θ) = u(θ) − u0 :

   A_PQ(u(θ)) ≤ A0 + G_x·d_x + G_y·d_y + (G_x²·d_x² + 2G_x·G_y·d_x·d_y + G_y²·d_y²)/(4A0).

4. On intègre sur I = [t0, t1], t_k = x_k·π. Les moments sont :
   - h = ∫1 = t1 − t0 ;
   - I_c = ∫cos = sin t1 − sin t0 ;
   - I_s = ∫sin = cos t0 − cos t1 ;
   - I_cc = ∫cos² = h/2 + (sin 2t1 − sin 2t0)/4 ;
   - I_ss = ∫sin² = h/2 − (sin 2t1 − sin 2t0)/4 ;
   - I_cs = ∫cos·sin = (sin² t1 − sin² t0)/2.

   Ce sont les primitives exactes, vérifiées : (θ/2 + sin 2θ/4)' = cos² θ et (sin² θ/2)' = sin θ·cos θ. C'est `moments` (`certifier/geometry.py`).
5. Les moments centrés (`core.box_bound`) sont exacts algébriquement :
   - J1x = I_c − x0·h ;
   - Jxx = I_cc − 2x0·I_c + x0²·h ;
   - Jxy = I_cs − x0·I_s − y0·I_c + x0·y0·h ;
   - et de même J1y, Jyy (ici (x0, y0) = u0).

   Ce sont les intégrales de d_x, d_x², d_x·d_y, etc.
6. B = S0·h + SGx·J1x + SGy·J1y + Mxx·Jxx + 2Mxy·Jxy + Myy·Jyy + Smink·h est une boule Arb. Les t_k = arb(x_k)·arb.pi() contiennent les vraies valeurs x_k·π, donc B contient la vraie valeur de Σ_{M1} ∫_I T² + Σ_{M2} a_K·(x1 − x0)·π.
7. `fmpq_upper(B)` majore donc ∫_I Σ_{actives} A_PQ(u(θ)) dθ.

### c.6 La majoration (M2)

**Rectangle.** `core.arc_rectangle(t0, t1)` donne un rectangle rationnel K ⊇ {u(θ) : θ ∈ [x0π, x1π]}, pour [x0, x1] ⊆ [0, 1].
- cos est décroissante sur [0, π], d'où x ∈ [cos t1, cos t0].
- sin est concave sur [0, π], donc son minimum est atteint aux extrémités.
- Son maximum vaut max(sin t0, sin t1) si t1 < π/2 ou t0 > π/2 (comparaisons Arb « certainement vraies »), et ≤ 1 sinon.
- Les bornes rationnelles sont prises par `fmpq_lower`/`fmpq_upper` des boules.

**Borne.** Pour u ∈ K, on a Q − u ⊆ Q ⊕ (−K), d'où A(u(θ)) ≤ aire(P ∩ (Q ⊕ (−K))) =: a_K, un rationnel exact. `minkowski(pr.Q, negate(K))` est l'enveloppe des q − k, c'est-à-dire Q ⊕ (−K) ; `intersection` est exacte. On intègre : a_K·h.

La borne est valable quel que soit A0. Elle sert quand A0 = 0 (`use_m2`), ou par choix flottant quand elle est meilleure (comparaison avec `quad_threshold`). Le choix n'affecte pas la validité, puisque les deux sont des majorants.

### c.7 Assemblage

- Les boîtes forment une partition exacte de [0, 1] ; `certifier/recompute.py` le vérifie, et `verifier/verify.py` (étape E6) le vérifie indépendamment.
- Par (b) et c.5–c.6, Σ_boîtes `box_bound` ≥ ∫_0^π Σ_{(P,Q)} A_PQ(u(θ)) dθ.
- `certifier/certify.py` et `certifier/recompute.py` forment arb(Σ)/(arb.pi()·arb(|C|)) et en prennent la borne supérieure dyadique (`fmpq_upper`) ; `certify.py` en déduit le majorant lisible k/10¹⁰ (assertion exacte `readable >= p_up`), et `recompute.py` vérifie que la borne recalculée est ≤ ce majorant. `verifier/verify.py` (E6) refait l'arithmétique finale en `Fraction` avec π > 314159265358979/10¹⁴.
- Avec 0.2 et (d), on obtient p5(c) ≤ ce majorant.

---

## (d) Symétrie θ → θ + π et normalisation [DÉMONTRÉ ICI]

**Proposition d.1.** Pour toute coloration mesurable G-périodique c, on a p(θ + π) = p(θ).

*Preuve.*
1. u(θ + π) = −u(θ) =: −u. Soit τ : T → T, x ↦ x + u, la translation du tore T = ℝ²/G (c est G-périodique, donc définie sur T). Elle préserve la mesure de Haar.
2. Soit E(v) = {x ∈ T : c(x) = c(x + v)}. On a τ(E(u)) = {y : c(y − u) = c(y)} = {y : c(y) = c(y + (−u))} = E(−u).
3. **Échange des deux extrémités du segment.** Le segment {x, x + u} et le segment {y, y − u} avec y = x + u sont le même ; la position uniforme de l'origine est préservée par τ.
4. Donc mes E(−u) = mes E(u), c'est-à-dire p(θ + π) = p(θ). ∎

Aucune autre symétrie n'est utilisée. θ → −θ et θ → θ + π/3 ne sont pas des symétries de DISQ ou d'ILE, et le code ne s'en sert pas : il intègre toute la plage [0, π].

**Normalisation.** Par d.1, (1/2π)∫_0^{2π} p = (1/2π)·2·∫_0^π p = (1/π)∫_0^π p. Par 0.2, p(θ) = |C|⁻¹·Σ A_PQ(u(θ)). D'où

  **p5(c) = (1/(π|C|)) ∫_0^π Σ_{(P,Q)} A_PQ(u(θ)) dθ**,

et c'est exactement la division `arb(tot) / (arb.pi() * arb(cfg.cell_area))` (`certifier/certify.py`, `certifier/recompute.py`), où tot majore ∫_0^π Σ A (c.7). Le cas test BANDES (`certify.py BANDES`, coloration `config_strips`) confirme numériquement la normalisation : p = 1 − 2/π. [VÉRIFIÉ NUMÉRIQUEMENT en session 2.]

---

## 5. Écarts de détail entre le code et la rédaction de la certification (aucun n'affecte la validité)

La rédaction de référence est celle de la session 2, reprise sous forme condensée à la section 4 de `note/v6_45.tex`.

1. **« Énumération des paires ».** Le texte dit « rayon 1 + |z_i − z_j| + r_i + r_j ». Le code prend le majorant global 1 + max|z_i − z_j| + 2·max r (`core.radius_bound`), puis le filtre par couple à 1 + r_i + r_j. C'est équivalent en effet, et prudent.
2. **« Paires actives ».** « secteur + 2k, k ∈ {−2, …, 2} » correspond, dans le code (`core.active`), aux décalages {−4, −2, 0, 2, 4} (en unités de π). C'est cohérent ; seuls 0 et 2 peuvent servir (b.3).
3. **`is_regular`.** Sa docstring la présente comme une « condition suffisante » de différentiabilité. C'est exact ; elle est par ailleurs exactement la régularité du théorème c.4.5. Elle rejette aussi des segments colinéaires disjoints, ce qui est vrai et sans conséquence.
4. **Énumération.** Le code va jusqu'à |a|, |b| ≤ 2, alors que |a|, |b| ≤ 1 suffit (théorème a.2) : c'est un excès de prudence.
5. **`clip`.** La version de la session 2 contenait une expression conditionnelle sans effet (deux branches égales) ; elle a disparu du code distribué (`otag.append(tags[i])`). Le comportement est le même et il est le bon (c.4.7).
6. **Docstring de `certifier/geometry.py`.** Elle renvoie aux preuves de la « note, Section 4 », ce qui est correct (section « Certification of p5 » de `note/v6_45.tex`). L'ancienne docstring renvoyait à un mauvais paragraphe.
7. **(M1).** S = {A > 0} = int(Q − P) est vrai, mais seule l'inclusion S ⊆ int M (lemme b.1) sert. La concavité est démontrée sur S lui-même, sans passage à la fermeture.
8. **Convexité.** Depuis la relecture de session 3 (trou T1), le test de convexité du code est `is_strictly_convex` (virages positifs **et** égalité à l'enveloppe convexe), dans `core.verify` et dans `verifier/verify.py` (E1). Le lemme 0.0 montre qu'il garantit la convexité stricte.

## 6. Points restant [À VÉRIFIER]

- **Sémantique d'Arb** (python-flint 0.9.0) : les boules renvoyées contiennent la valeur exacte. C'est une hypothèse standard, documentée au niveau de FLINT/Arb (`relecture_preuves.md`, §3(i)), non démontrée ici.
- **Définition de p_k(c) chez Gwyn–Stavrianos** et identification avec (1/2π)∫p(θ) dθ : relue dans `relecture_preuves.md`, §3(ii) ; non encore relue par un mathématicien.
- **Correction de la chaîne monotone d'Andrew** (`hull`) : algorithme classique, utilisé tel quel ; le vérificateur indépendant en a sa propre implémentation.
- **Relecture humaine** : l'ensemble de ces preuves n'a été relu que par des agents d'IA.

---

## Mise à jour du 15 novembre 2026 (session 4)

Un audit externe n'a trouvé aucune erreur mathématique, mais a demandé que ce fichier décrive le **code distribué**. Les changements sont les suivants ; la version de la session 3 est conservée à part, sans modification.

1. **Convexité.** Nouveau §0.0 : description du test réellement utilisé, `is_strictly_convex` (`certifier/geometry.py`) et `strictly_convex` (`verifier/verify.py`, E1) : virages positifs **et** égalité, à rotation cyclique près, avec l'enveloppe convexe. Lemme 0.0 : ce test garantit la convexité stricte. (V1) au §0.1 renvoie désormais à ce test.
2. **Signe (théorème a.2, partie 1, étape 2).** L'identité correcte est det(g2, t) = det(g2, y − x) − det(g2, y' − x), puisque t = (y − x) − (y' − x) ; la majoration en valeur absolue est inchangée.
3. **Proposition b.3, étape 1.** « u ∈ M donc d2 > 0 » est remplacé par l'argument correct : la paire est dans la branche `else` de `if d2 == 0` de `core.enumerate_pairs` (c'est ce que force `active` faux, via `pr.always` faux), d'où d2 > 0 et 0 ∉ M ; u ∈ M sert seulement au lemme b.3.
4. **Gradient.** Le §c.4 est réécrit : formule exacte de l'accroissement (c.4.1–c.4.3), continuité des longueurs ℓ_f (c.4.4), différentiabilité et formule ∇A(u0) = −Σ_f ν_f |f ∩ P| (c.4.5), test codé (c.4.6), et lien avec l'étiquetage de Sutherland–Hodgman de `clip`/`intersection`/`area_and_gradient` (c.4.7). Correspondance de numérotation avec la session 3 : ancien c.4.1 (gradient distributionnel) → nouveaux c.4.1–c.4.3 ; ancien c.4.2 → c.4.4 ; ancien c.4.3 → c.4.5 ; ancien « test codé » → c.4.6 ; ancien c.4.4 → c.4.7.
5. **Renvois.** Tous les renvois aux fichiers de travail des sessions 2 et 3 sont remplacés par les fichiers et fonctions du dépôt distribué (table de correspondance en tête). Les numéros de ligne sont supprimés : ils renvoient à des fichiers qui ne sont pas distribués.
6. **Publication.** Les chemins locaux et les commandes d'exécution propres à la machine de travail ont été retirés ; les chemins sont relatifs à la racine du dépôt.
7. **Statuts.** Les étiquettes sont [DÉMONTRÉ ICI], [CONNU + référence], [VÉRIFIÉ NUMÉRIQUEMENT], [À VÉRIFIER]. Les contrôles numériques de session 4 cités (pentagramme, identité de signe, gradient sur polygones aléatoires, identité d'accroissement) ont été exécutés avec les fonctions du dépôt, sans le modifier ; leur script n'est pas distribué.

## Compléments de la relecture indépendante (session 4 bis, 15 novembre 2026)

Une relecture par un sous-agent qui n'avait écrit ni le code ni ces preuves (`relecture_preuves_v4.md`) n'a trouvé
aucune erreur décisive. Elle demandait deux compléments, intégrés ici, et des formulations (lemme 0.0 étape 2 ; remarque
sur `hull` au § 0.0).

### Lemme 0.1 bis (aire calculée nulle ⟺ intersection d'intérieur vide) [DÉMONTRÉ ICI]

Soient P et K = Q − u deux polygones convexes à sommets rationnels, et I = P ∩ K. Si I est d'intérieur vide, l'aire
calculée par `area(intersection(P, Q − u))` est nulle (ou `intersection` renvoie moins de 3 sommets).

*Preuve.* `intersection` coupe P successivement par les demi-plans de K, avec `clip`. Chaque sommet émis par `clip` est
soit un sommet du polygone d'entrée qui vérifie le demi-plan, soit le point d'intersection d'une arête d'entrée avec la
droite de coupe. Dans les deux cas, il appartient au polygone d'entrée et au demi-plan fermé. Par récurrence sur les
demi-plans, tous les sommets de la sortie finale appartiennent à I. Si I est d'intérieur vide, c'est un ensemble convexe
contenu dans une droite (vide, un point ou un segment) : tous les sommets de la sortie sont alignés, et la formule du
lacet donne une aire nulle. Les calculs sont rationnels exacts : aucun arrondi n'intervient. ∎

Avec le lemme SH (aire vraie > 0 ⇒ sortie = bord exact de I), on obtient : **aire calculée > 0 ⟺ aire vraie > 0**, et
l'aire calculée est alors l'aire exacte. C'est ce qu'utilisent `core.verify` (§ 0.1), le choix `use_m2 = (A0 == 0)` de
`core.box_bound` (borne (M1) appliquée seulement si A0 > 0 est vrai) et la borne (M2).

### Contrôles numériques non distribués

Les mentions [VÉRIFIÉ NUMÉRIQUEMENT] suivantes renvoient à des scripts de contrôle des sessions 3 et 4, **qui ne sont
pas dans ce dépôt**. Elles sont donc **non reproductibles depuis le dépôt**, et aucune n'est nécessaire à la preuve :
- le pentagramme rejeté par `is_strictly_convex` (§ 0.0) ;
- les tirages exacts de l'identité de signe du § (a) ;
- les comparaisons du gradient (`area_and_gradient` contre Cyrus–Beck ou contre des différences finies) et l'identité
  d'accroissement du § (c).4 ;
- les distances minimales toutes couleurs de la session 3.

Les seuls contrôles reproductibles depuis le dépôt sont ceux de `verifier/verify.py` (E1–E6, N), de
`certifier/recompute.py` et de `verifier/u_bounds.py`.
