# Relecture indépendante (v4) de `proofs/preuves.md` et `proofs/relecture_preuves.md`

Relecteur indépendant : je n'ai écrit ni le code ni les preuves. Tout a été lu en **lecture seule**. Je n'ai modifié aucun fichier du dépôt et je n'ai fait aucun commit.

- **Date** : 2026-11-15.
- **Début** : 19:53:39 ; **fin** : 19:58:46 (commande `date`). La relecture a donc duré environ 5 minutes d'horloge. C'est nettement moins que les 45 minutes prévues ; je n'ai pas d'autre journal que ces deux horodatages.
- **Version relue** : la dernière version des deux fichiers, celle du commit `6ff1d21`, sans modification locale dans `proofs/`. J'ai vérifié avec `git diff 3af8dfe` (diff vide) que le code de `certifier/` et de `verifier/` n'a pas changé depuis `3af8dfe`, comme les fichiers l'affirment.
- **Chemins** : ils sont relatifs à la racine du dépôt.

## Fichiers lus en entier

- `proofs/preuves.md` et `proofs/relecture_preuves.md` ;
- `certifier/geometry.py`, `certifier/core.py`, `certifier/certify.py`, `certifier/recompute.py` et `verifier/verify.py` ;
- la section 4 (« Certification of p5 ») de `note/v6_45.tex` ;
- pour `certifier/colourings.py` et `certifier/island.py`, seulement les noms de fonctions et `cell_area`, par grep.

## Contrôles exécutés

J'ai exécuté deux petits scripts (bibliothèque standard, python-flint 0.9.0 et les fonctions du dépôt importées sans modification). Ils ont tourné sous `systemd-run --user --scope -p MemoryMax=1200M -p MemorySwapMax=0`, dans le scratchpad, et ne sont pas distribués.

1. **Convexité.** Résultats identiques pour `is_strictly_convex` et pour `verify.strictly_convex` :
   - un pentagone est accepté ;
   - les cas suivants sont rejetés : pentagramme (que `all_left_turns` accepte), parcours dans le sens horaire, sommet répété, sommet aligné, carré parcouru deux fois (que `all_left_turns` accepte aussi).
2. **Gradient.** J'ai comparé `area_and_gradient` à des différences finies exactes en `fmpq`, avec h = 10⁻⁹ et h = 10⁻¹², dans des positions **dégénérées mais régulières** :
   - sommets de P sur des arêtes de Q − u0, sommets confondus, Q − u0 intérieur à P avec arêtes parallèles ;
   - 160 cas aléatoires où un sommet de P est placé exactement sur une arête de Q − u0.

   Résultat : 0 échec. L'écart observé est d'ordre O(h²), comme attendu. En position **non régulière** (arêtes colinéaires), le gradient renvoyé est faux, comme prévu ; c'est le cas que le code évite.
3. **Aire nulle.** Dans trois cas de contact (par une arête, par un sommet, sommet contre arête), `area_and_gradient` renvoie une aire égale à 0.
4. **Identité de signe de (a).** det(g2, t) = det(g2, y − x) − det(g2, y′ − x) = a·det(g2, g1) est vraie sur 1000/1000 tirages rationnels exacts.
5. **Étapes E1, E2 et E4 sur les JSON distribués.** Avec les fonctions de `verifier/verify.py` :
   - convexité : 52/52 et 260/260 ;
   - Σ aires = |C| exactement ;
   - condition de E4 fausse pour k = 1 et vraie pour k = 2 ;
   - marges 3,9024 et 3,9024 (DISQP32), 3,8850 et 3,8141 (ILEP256). Ce sont les valeurs annoncées.

## Points vérifiés

### 1. §0.0, test de convexité stricte

La description correspond **exactement** au code, dans les deux fichiers :
- `is_strictly_convex` vaut `all_left_turns(P)` et `equals_cyclically(list(P), hull(P))` ;
- `hull` trie `set(points)` et retire les points alignés par `<= 0` ;
- `verify.strictly_convex` fait le même calcul avec `same_cyclic`.

La preuve du lemme 0.0 est correcte :
- la rotation cyclique d'une liste de points distincts n'a pas de répétition ;
- la longueur commune n ≥ 3 interdit le cas aligné ;
- l'orientation directe et l'absence de points alignés viennent de la chaîne monotone.

Les deux `hull` sont la même implémentation, ligne pour ligne. Je l'ai relue : c'est la chaîne monotone standard, et elle est correcte. Voir la remarque F2.

### 2. (a), complétude des translations

- **Identité.** t = y − y′ = (y − x) − (y′ − x), donc det(g2, t) = det(g2, y − x) − det(g2, y′ − x). C'est juste.
- **Projection.** |det(g2, t)| = |a|·|det(g2, g1)| = |a|·|C| ≤ |t|·|g2|. C'est juste.
- **Cohérence avec `translation_bounds`.** La boucle donne le plus grand amax tel que amax²·|C|² ≤ ρ²·|g2|² (et bmax avec |g1|²), avec `cell_area = abs(det)`. C'est cohérent.
- **Rayons.** ρ = `radius_bound(balls, 0)` dans `verify`, et ρ′ = `radius_bound(balls, 1)` dans `enumerate_pairs`. Les majorations sont vérifiées exactement par les `assert`.
- **E4.** `dt(g, v)` = det(g, v) ; W est la largeur sur tous les sommets de F. La condition (k|C| − W)² > |g|² avec k|C| − W > 0 est bien monotone en k. E5 parcourt |a|, |b| ≤ A_s − 1 = 1.
- **Valeurs numériques.** Les valeurs du tableau sont cohérentes entre elles (2|C| − W2 = 2,78624, etc.) et avec le contrôle 5.

### 3. (b.3), « d2 > 0 vient de la branche »

L'argument correspond au code :
- `active` renvoie vrai dès que `pr.always` est vrai. Donc `active` faux implique `pr.always` faux, ce qui implique la branche `else` de `if d2 == 0`.
- `dist2_origin_polygon` ne renvoie 0 que par le test `inside`. Sinon, une arête vérifie cross < 0 : l'origine est strictement à l'extérieur, et le minimum renvoyé est > 0.
- M sort de `hull` : il est orienté dans le sens direct et a au moins 3 sommets.
- Autres points vérifiés :
  - le lemme du secteur (quasi-linéarité de tan β, valeur principale de β(w) − β(ref), qui est dans (−π, π)) ;
  - les encadrements `fmpq_lower`/`fmpq_upper` et le sens des inégalités pour a0 et a1 ;
  - 2k ∈ (−2, 3), donc 2k ∈ {0, 2} ;
  - la négation exacte du test `x1 < a0 + k or x0 > a1 + k`.

  Aucune faute.

### 4. (c.4), formule du gradient

- **Lemme c.4.1.** J'ai revérifié les six positions de τ_e < τ_s par rapport à 0 < 1, ainsi que les signes σ_{f_e} = −1 et σ_{f_s} = +1. L'ensemble exclu N suffit :
  - D ne passe par aucun sommet ;
  - z et z + h ne sont pas sur ∂K ;
  - une droite qui touche K sans traverser son intérieur contient un sommet.
- **Lemme c.4.2.** Le jacobien det(ê, −h) = ⟨ν_f, h⟩ est juste, avec ν_f = (ê_y, −ê_x) en sens direct.
- **Proposition c.4.3.** L'accroissement est exact, sans hypothèse de régularité.
- **Lemme c.4.4.** La continuité des bornes de corde est juste. Le cas des arêtes parallèles est le seul où intervient la régularité (δ_e(u0) ≠ 0).
- **Théorème c.4.5.** La majoration du reste est o(|h|).
- **Signe.** ∇A(u0) = −Σ_f ν_f |f ∩ P| est confirmé par les différences finies du contrôle 2.
- **`parallel_edges` et `is_regular`.** La normalisation c_Q = c2/k est juste, y compris pour k < 0. Le cas k = 0 est impossible, car les arêtes ne sont pas dégénérées. `is_regular` est exactement la régularité.
- **Étiquetage dans `clip`.** Le code est conforme à la description :
  - `dp <= 0` : on émet p avec l'étiquette de l'arête, puis le point de sortie avec l'étiquette 1 si `dq > 0` ;
  - entrée : le point d'entrée reçoit l'étiquette de p → q ;
  - les doublons créés par dp = 0 ou dq = 0 sont des arêtes de longueur nulle, qui contribuent (0, 0) ;
  - une arête portée par la droite de coupe garde son ancienne étiquette. Si cette étiquette est 0, la régularité exclut le cas ; si elle est 1, il est impossible, car les droites des arêtes de Q − u0 sont distinctes.
- **Télescopage.** G = Σ des étiquettes 0 = −Σ des étiquettes 1 = −Σ_f ν_f ℓ_f(u0). C'est juste.
- **Cas limites.** Un sommet de P sur une arête de Q − u0, ou des sommets confondus, ne mettent pas la régularité en défaut et ne cassent pas la formule (contrôle 2). Seul point manquant : le cas d'aire nulle (voir C1).

### 5. (c.3) et (d)

- **(c.3).** A ≤ T² est juste dans les deux cas :
  - sur S, par concavité de φ sur [0, 1] et la majoration φ(1) ≤ φ(0) + φ′(0⁺), d'où T ≥ g ≥ 0 ;
  - hors de S (S est ouvert, donc le bord de S est hors de S), A = 0 ≤ T².

  Les formules algébriques de `box_bound` sont correctes : T² développé, Mxx, Mxy avec le facteur 2, Myy, ainsi que les moments J et les primitives de `moments`.
- **(d).** τ(E(u)) = E(−u) et la mesure de Haar est invariante : c'est juste. La normalisation 1/(π|C|) correspond à `arb(tot)/(arb.pi()*arb(cell_area))`. E6 utilise PI_LOW < π, ce qui va dans le bon sens.

### 6. Tables de correspondance

J'ai cherché par grep chaque fonction citée : `area`, `translate`, `cross`, `minkowski`, `intersection`, `moments`, `hull`, `all_left_turns`, `is_strictly_convex`, `equals_cyclically`, `negate`, `half_planes`, `clip`, `area_and_gradient`, `parallel_edges`, `is_regular`, `dist2_origin_polygon`, `max2_origin_polygon`, `subtract`, `clean`, `fmpq_upper`, `fmpq_lower`, `rational`, `translation_bounds`, `ball`, `radius_bound`, `verify`, `angle_arb`, `enumerate_pairs`, `active`, `active_float`, `F_float`, `p_float`, `arc_rectangle`, `box_bound`, `hexagon`, `hex_lattice`, `hexagon_reps`, `add_fifth_colour`, `config_strips`, `config_h4`, `ngon`, `config_disqp`, `build`, `config_ilep`, `work`, `main`, `smallest_k`, `strictly_separated`, `dist2`, `d2_point_segment`, `strictly_convex`, `same_cyclic` et `edge_separates`.

Toutes existent, dans le fichier indiqué. Les éléments suivants existent aussi :
- la classe `Pair`, avec l'attribut `always` ;
- les variables `use_m2`, `quad_threshold` et `stats["u0_attempts"]` ;
- l'attribut `cell_area` ;
- l'assertion `readable >= p_up` ;
- la ligne `otag.append(tags[i])`.

Les renvois internes vers `relecture_preuves.md` existent : §3(i), §3(ii) avec T2, §3(iii) avec le lemme SH, et T7.

### 7. Informations personnelles

J'ai cherché dans les deux fichiers les motifs suivants : `/home`, le nom de l'utilisateur, `Bureau`, `Donnees`, `@`, `/tmp` et `~/`. Aucune occurrence.

## Remarques

### DÉCISIF

Aucune.

### À COMPLÉTER

- **C1 — cas d'aire nulle de `intersection` et `area_and_gradient`.**
  - *Où.* `preuves.md` §0.1 (« `intersection` renvoie le polygone exact (§ (c).4.7) »), §c.5 point 2 et §c.6 ; `relecture_preuves.md` §3(iii), dernier paragraphe. Code : `core.box_bound` (`use_m2 = (A0 == 0)`), `core.verify` et la borne (M2).
  - *Le trou.* Le lemme SH et le lemme c.4.7 ne sont démontrés que si l'aire vraie est > 0. Or le code a aussi besoin de la réciproque : si l'aire vraie est nulle, l'aire calculée est nulle. Sans elle, (M1) pourrait être appliquée avec un A0 > 0 erroné, alors que la vraie aire en u0 est 0.
  - *La preuve.* Elle est courte. Par récurrence, chaque sommet émis par `clip` est dans l'intersection courante : p vérifie dp ≤ 0, ou bien le point est sur [p, q] avec d = 0. Tous les sommets de la sortie sont donc dans I. Si I est d'intérieur vide, ils sont alignés et l'aire du lacet vaut 0.
  - *Statut.* `relecture_preuves.md` l'affirme sans le démontrer. C'est vrai, et le contrôle 3 l'illustre. À ajouter en une phrase.
- **C2 — reproductibilité des contrôles cités.** Plusieurs [VÉRIFIÉ NUMÉRIQUEMENT] renvoient à des scripts non distribués : pentagramme, 1000 tirages de signe, 294 et 800 gradients, identité d'accroissement, distances toutes couleurs (`preuves.md` §0.0, (a), c.4.5, c.4.7 ; `relecture_preuves.md` §1.2 et section finale). Aucun n'est nécessaire à la preuve. La règle de reproductibilité du projet demande toutefois de conserver script, paramètres et sortie. À archiver, ou à étiqueter comme « non reproductible depuis le dépôt ».

### FORMULATION

- **F1 — `preuves.md` §0.0, lemme 0.0, étape 2.** « comme n ≥ 3 (`all_left_turns`), S = set(P) n'est pas aligné » : n ≥ 3 points peuvent être alignés. La bonne justification est l'une des deux suivantes : len(hull(P)) = n ≥ 3, alors qu'une enveloppe d'un ensemble aligné a au plus 2 points ; ou bien un virage strictement positif. La conclusion est juste.
- **F2 — `preuves.md` §0.0 et §6.** Le `hull` de `verifier/verify.py` est la même implémentation que celui de `certifier/geometry.py`. Le vérificateur est donc indépendant par le code (Fraction, pas de flint), mais pas par l'algorithme. Une erreur d'implémentation de la chaîne monotone serait commune aux deux. Je l'ai relue et elle est correcte ; il vaut mieux le dire.
- **F3 — `preuves.md` (d), proposition d.1, étape 3.** La phrase n'apporte rien (déjà noté T9, non appliqué). Elle est sans danger.
- **F4 — `preuves.md` b.3, étape 1.** « d2 > 0 puisque d2 est un carré de distance » : il serait plus précis d'écrire « d2 ≠ 0 et d2 ≥ 0 (minimum de sommes de carrés), et `inside` a échoué ». Le fond est juste.
- **F5 — `preuves.md` c.5, point 1.** La boucle `while True` de `box_bound` n'a pas de terminaison démontrée. Cela n'affecte pas la validité : si elle termine, u0 est régulier. Les journaux indiquent 0 déplacement. On pourrait le dire.

## Verdict global

Je n'ai trouvé aucune erreur DÉCISIVE. Le §0.0, (a), (b.3), (c.3), (c.4) et (d) sont corrects et décrivent exactement le code. Il reste deux compléments mineurs : le cas d'aire nulle de l'intersection (C1) et l'archivage des scripts de contrôle (C2).
