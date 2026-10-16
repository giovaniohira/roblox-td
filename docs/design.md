# Roblox TD — Game Design (MVP)

> Todos os números são valores iniciais para playtest. Nada aqui está balanceado.

## 1. Visão geral

Tower defense em que as torres são espíritos elementais invocados por gacha antes da run. A progressão permanente segue o modelo de Summoners War: nível, evolução, despertar, skills e runas.

**Princípio de duas camadas**

- **Meta (permanente):** nível, estrelas, despertar, skill-ups e runas. Define *quanto* cada torre bate.
- **Run (temporária):** ouro, posicionamento, tiers comprados na partida e ativas. Define *onde e quando* cada torre bate.
- A meta multiplica a base e o jogador decide a run. Status sozinho não vence um andar alto, e boa colocação sozinha não vence também.

```
dano = (base × mult_nível_estrela × (1 + ATK%_runas) + ATK_flat_runas)
       × mult_tier_run × mult_elemento × crit × (1 − armadura_efetiva)
```

**Escopo do MVP**

- 1 mapa, 10 andares de dificuldade (B1–B10), 50 waves por run.
- 5 famílias × 5 elementos = **25 torres**, cada uma com passiva, ativa e skill de líder próprias.
- Modos: solo e coop (2–4 jogadores). O x1 DPS fica desenhado, mas não entra no MVP (seção 12).

## 2. Direção de arte

- **Estilo:** espíritos elementais chibi, inspirados em Summoners War. Proporção de cabeça grande, silhuetas legíveis de longe e shading tipo toon. Projeto do zero, sem reaproveitar assets de outros jogos.
- **Cores por elemento** (usadas em VFX, UI, bordas de carta e no preview de waves):

| Elemento | Cor |
|---|---|
| Fogo | `#FF6A3D` |
| Água | `#3DA5FF` |
| Vento | `#4CD98A` |
| Luz | `#FFD84A` |
| Trevas | `#8A4DFF` |

- **Escopo de assets:** 5 rigs (um por família) × 5 skins elementais = 25 modelos. No MVP, a versão desperta é o mesmo rig + acessório + aura de VFX, e não um modelo novo.
- **Mapa:** santuário elemental em ruínas, com caminho único e pontos de colocação livres. Os inimigos são espíritos corrompidos.

## 3. Loop principal

1. **Lobby:** invocar (gacha), subir nível, evoluir, despertar e equipar runas.
2. **Pré-run:** escolher o andar (B1–B10) e o loadout de **4 torres**. A torre do slot 1 é a líder.
3. **Run:** 50 waves, com baú nas waves 10/20/30/40/50.
4. **Autofarm:** depois de limpar um andar, ele vira uma barra de progresso que dropa runas (seção 5).
5. **Pós-run:** gastar o loot e tentar um andar maior ou limpar o mesmo andar mais rápido.

O loop se fecha assim: andar maior dropa runa melhor, runa melhor limpa mais rápido, e limpar mais rápido acelera o autofarm.

## 4. Run

### 4.1 Estrutura das 50 waves

| Waves | Conteúdo |
|---|---|
| 1–9, 11–19, ... | Inimigos comuns. A cada 5 waves, uma wave de elite |
| 10, 20, 30, 40 | Chefe com elemento + baú |
| 50 | Chefe final em 3 fases (troca de elemento a cada fase) + baú grande |

- O preview mostra os elementos das próximas waves antes da run e durante ela.
- Dificuldade por andar: HP dos inimigos × `1.45^(andar − 1)` (B10 ≈ 28×).

### 4.2 Primeira run vs repetição

- **Primeira run de um andar:** run normal, com o cooldown fixo de 15 s entre waves.
- **Repetição (andar já limpo):** libera o botão **Chamar próxima wave**. O jogador pode chamar waves antes da hora e empilhá-las no caminho. No coop, a chamada é por voto da maioria.
- O **tempo de limpeza** é medido em tempo de simulação, não em tempo real, para que a velocidade 2x não distorça o recorde. Esse tempo é a métrica de DPS que alimenta o autofarm e os leaderboards.

### 4.3 Economia na run

- Ouro por kill + renda passiva por wave. O ouro zera no fim da run.
- Limite de **12 torres colocadas** no solo e de **12 / n por jogador** no coop (arredondado para cima).
- Tiers na partida:

| Tier | Mult. ATK | Custo (× custo base) | Requisito |
|---|---|---|---|
| 0 (colocar) | 1.0 | 1.0 | — |
| 1 | 1.4 | 1.2 | — |
| 2 | 1.9 | 2.0 | — |
| 3 | 2.6 | 3.2 | — |
| 4 | 3.5 | 5.0 | — |
| 5 | 5.0 | 8.0 | **Torre desperta** |

- Base: 100 de vida. Inimigo comum que vaza tira 1, elite tira 5, chefe tira 25.

### 4.4 Coop (2–4 jogadores)

- Vida da base compartilhada, ouro individual e loot individual.
- HP dos inimigos × `1 + 0.65 × (n − 1)`.
- **Auras** (Tanuki, buffs) afetam as torres de todos. **Líder** afeta só as torres do dono.
- Tela final com o medidor de dano por jogador (o x1 reaproveita esse medidor).

## 5. Autofarm

- Liberado por andar depois da primeira vitória (wave 50).
- **Só solo e só online:** a barra só avança enquanto o jogador estiver dentro do quadrado AFK do lobby. Sair do quadrado, entrar numa run ou sair do jogo pausa a barra. Não existe progresso offline.
- O jogador escolhe **um** andar já limpo para o autofarm. O padrão é o mais alto.
- Cada barra completa dropa **1 runa** da tabela daquele andar + uma pequena quantia de mana + 1 poção de XP.
- Duração da barra = `max(2 min, melhor_tempo_solo × 1.0)`.
- Só vale o recorde de **runs solo**. Tempo de coop não conta para o autofarm.
- O autofarm dá **só runas, mana e XP**. Essências e fragmentos exigem jogar runs ativas.
- **Risco técnico:** o Roblox desconecta jogadores ociosos depois de cerca de 20 min. É preciso validar uma solução, por exemplo detectar o evento `Idled` e reconectar o jogador no lobby sem perder a barra.

**Decisão que o sistema cria:** farmar um andar alto (runas melhores, barra mais lenta) ou um andar baixo limpo rápido (mais runas, raridade menor).

## 6. Progressão meta

### 6.1 Nível

- Teto de nível por estrela: 1★ 15 · 2★ 20 · 3★ 25 · 4★ 30 · 5★ 35 · 6★ 40.
- XP vem de: torres do loadout ganham XP nas runs, e poções de XP (do autofarm) servem para torres no banco.
- `ATK(nível) = ATK_base × (1 + 0.06 × (nível − 1))`.

### 6.2 Evolução (por fragmento)

- Requisito: nível máximo + Fragmentos Estelares + mana.
- Os fragmentos são genéricos (servem para qualquer torre) e dropam nos baús das runas ativas.

| Evolução | Fragmentos | Mana |
|---|---|---|
| 3★ → 4★ | 20 | 10k |
| 4★ → 5★ | 50 | 40k |
| 5★ → 6★ | 120 | 150k |

- Cada estrela acima da natural dá +15% em todos os status base. Ao evoluir, o nível volta para 1.

### 6.3 Skill-up

- Cópias repetidas do gacha sobem a ativa em até +4 níveis, cada nível dando −8% de cooldown e +10% de efeito.
- Cópias além do máximo viram 10 Fragmentos Estelares.

### 6.4 Despertar

- Custo: essência do elemento da torre + Essência Arcana + mana.
- Efeitos: +20% ATK base, +10% de alcance, ativa melhorada (+50% de efeito *ou* −20% de cooldown, definido por torre), **desbloqueia o tier 5 na run**, e a torre ganha nome novo e visual desperto.
- Essências dropam nas runs ativas, de acordo com o elemento do dia (seção 7).

### 6.5 Runas

- **Raridade** (número de substats iniciais): Normal 0 · Mágica 1 · Rara 2 · Herói 3 · Lendária 4.
- **Upgrade** de +0 até +15 com mana e chance de falha crescente. A cada +3, ganha um substat novo (até 4) ou melhora um existente.
- **Atributos principais por slot:**

| Slot | Principal | +0 → +15 |
|---|---|---|
| 1 | ATK flat (fixo) | 22 → 160 |
| 2 | ATK% ou Vel. ataque% | 4% → 63% / 3% → 30% |
| 3 | Alcance% (fixo) | 2% → 20% |
| 4 | ATK%, Taxa crit ou Dano crit | 4% → 63% / 4% → 58% / 6% → 80% |
| 5 | Vel. ataque% (fixo) | 2% → 15% |
| 6 | ATK%, Precisão ou Dano vs chefe | 4% → 63% / 4% → 64% / 4% → 50% |

- **Substats possíveis:** ATK flat, ATK%, Vel. ataque%, Alcance%, Taxa crit, Dano crit, Precisão, Dano vs chefe.
- **Sets do MVP:**

| Set | Peças | Bônus |
|---|---|---|
| Violento | 4 | 20% de chance de ataque extra |
| Fúria | 4 | +40% de dano crítico |
| Rapidez | 4 | +25% de velocidade de ataque |
| Lâmina | 2 | +12% de taxa de crítico |
| Foco | 2 | +20% de precisão (chance de aplicar efeitos) |
| Ganância | 2 | +15% de ouro por kill desta torre |

- **Drop por andar:**

| Andar | Raridade máxima |
|---|---|
| B1–B3 | Mágica |
| B4–B6 | Rara |
| B7–B9 | Herói |
| B10 | Lendária (5%) |

- Inventário de 300 runas. Runa vendida vira mana.

### 6.6 Líder

- A torre do slot 1 aplica sua skill de líder às torres do dono. Líderes não acumulam.

## 7. Elementos

- **Ciclo:** Fogo > Vento > Água > Fogo, e Luz ⇄ Trevas (uma tem vantagem sobre a outra, nos dois sentidos).
- **Vantagem:** +30% de dano.
- **Desvantagem:** −30% de dano e golpe raspado (sem crítico e sem aplicar efeito).
- Todo inimigo tem elemento.
- **Rotação diária:** num dia de elemento, 60% das waves são daquele elemento e dropam a essência dele.

| Dia | Elemento |
|---|---|
| Segunda | Fogo |
| Terça | Água |
| Quarta | Vento |
| Quinta | Luz |
| Sexta | Trevas |
| Sábado e domingo | Todos (dropa Essência Arcana em dobro) |

## 8. Torres

### 8.1 Famílias

| Família | Papel | ★ natural | Alcance | Ataques/s | ATK base | Alvo |
|---|---|---|---|---|---|---|
| Pixie | Atiradora (alvo único) | 3★ (Luz/Trevas 4★) | 30 | 1.2 | 100 | Mais avançado |
| Coruja | Controle | 3★ (Luz/Trevas 4★) | 20 | 0.8 | 50 | Mais avançado |
| Dragãozinho | Dano em área | 4★ (Luz/Trevas 5★) | 18 | 0.5 | 120 | Splash, raio 6 |
| Tanuki | Suporte/economia | 4★ (Luz/Trevas 5★) | Aura 15 | 0.6 | 40 | Mais avançado |
| Kitsune | Matadora de chefe | 5★ | 22 | 0.7 | 160 | Maior HP |

Alcance em studs. A identidade de cada elemento se repete entre as famílias:

| Elemento | Identidade |
|---|---|
| Fogo | Queimadura e explosão |
| Água | Lentidão e congelamento |
| Vento | Velocidade e quebra de armadura |
| Luz | Marca, buff, ouro e remoção de escudo |
| Trevas | Dano em % do HP e execução |

### 8.2 Pixie (atiradora)

| Elem. | Passiva | Ativa (CD) | Líder |
|---|---|---|---|
| Fogo | Tiros aplicam Queimadura (5% ATK/s por 4 s, acumula 5×) | **Chuva de Brasas** (25 s): 10 flechas em inimigos aleatórios no alcance, cada uma com 2 acúmulos de Queimadura | +15% ATK nas torres de Fogo |
| Água | 25% de chance de Lentidão (−30% vel., 2 s) | **Tiro Glacial** (30 s): congela o inimigo mais avançado por 2.5 s (chefe: −50% vel.) | +10% de alcance em todas |
| Vento | A cada 4º tiro, dispara 2 flechas extras em alvos próximos | **Rajada** (30 s): +100% de vel. ataque por 6 s | +15% vel. ataque nas torres de Vento |
| Luz | Críticos aplicam Marca (+20% de dano recebido, 3 s) | **Flecha Sagrada** (35 s): atravessa o caminho em linha, 600% ATK em todos que acertar | +12% de taxa crit em todas |
| Trevas | +1% de dano para cada 2% de HP que falta no alvo | **Flecha da Ruína** (40 s): executa até 3 inimigos comuns abaixo de 25% HP. Em chefe, 400% ATK | +20% de dano crit em todas |

### 8.3 Coruja (controle)

| Elem. | Passiva | Ativa (CD) | Líder |
|---|---|---|---|
| Fogo | A Queimadura dela bloqueia regeneração e cura | **Anel de Fogo** (30 s): círculo no caminho por 6 s. Quem cruza fica atordoado 1 s (uma vez por inimigo) | +15% de precisão em todas |
| Água | Ataques causam Lentidão de −35% em área (raio 4) | **Nevasca** (40 s): congela todos no alcance por 2 s (chefe 0.5 s) | +15% ATK nas torres de Água |
| Vento | 20% de chance de atordoar por 0.8 s | **Ventania** (35 s): empurra até 5 inimigos comuns 20 studs para trás no caminho | +10% vel. ataque em todas |
| Luz | Inimigos sob qualquer controle recebem +20% de dano | **Selo Sagrado** (45 s): prende o chefe por 2 s e remove o escudo dele | +20% de duração nos controles |
| Trevas | Ataques aplicam Silêncio por 3 s (o inimigo não cura, não cria escudo e não invoca) | **Pavor** (40 s): os inimigos no alcance andam para trás por 1.5 s | Chefes com −10% de velocidade |

### 8.4 Dragãozinho (área)

| Elem. | Passiva | Ativa (CD) | Líder |
|---|---|---|---|
| Fogo | Inimigos mortos por ele explodem (30% ATK em área) | **Meteoro** (35 s): zona de fogo no caminho por 5 s, 80% ATK/s | +15% de dano em área em todas |
| Água | O splash aplica Encharcado (−20% vel., 3 s) | **Maré** (40 s): onda que empurra todos no alcance 10 studs para trás | Inimigos com −8% de velocidade |
| Vento | Raio do splash +50% | **Tornado** (40 s): puxa os inimigos para um ponto por 3 s, 50% ATK/s | +15% ATK nas torres de Vento |
| Luz | Um sopro que acerta 3+ inimigos gera +1 de ouro | **Sopro Radiante** (35 s): remove o escudo de todos no alcance e causa 300% ATK | +15% ATK nas torres de Luz |
| Trevas | O splash reduz a armadura em 10% (acumula 3×, 5 s) | **Chama Negra** (45 s): causa 8% do HP máx de cada inimigo no alcance (chefe 3%) | +15% ATK nas torres de Trevas |

### 8.5 Tanuki (suporte/economia)

| Elem. | Passiva | Ativa (CD) | Líder |
|---|---|---|---|
| Fogo | Aura: +15% ATK nos aliados | **Tambor de Guerra** (45 s): a aura vira +40% ATK por 8 s | +10% ATK em todas |
| Água | Aura: +15% vel. ataque nos aliados | **Chuva Restauradora** (60 s, 1× por wave): cura 5% da vida da base | Base com +20% de vida |
| Vento | Aura: +15% de alcance nos aliados | **Bênção do Vento** (60 s): zera o cooldown das ativas dos aliados na aura (menos Tanukis) | −10% de cooldown nas ativas |
| Luz | Gera ouro no fim de cada wave (escala com o tier) | **Moeda da Sorte** (1× a cada 3 waves): na próxima wave, +50% de ouro por kill para o dono | +10% de ouro por kill |
| Trevas | Aura: os aliados ignoram 25% da armadura | **Pacto Sombrio** (60 s): consome 5% da vida da base e dá +60% de dano aos aliados na aura por 10 s | +10% de dano contra chefes |

### 8.6 Kitsune (matadora de chefe)

| Elem. | Passiva | Ativa (CD) | Líder |
|---|---|---|---|
| Fogo | Cada acerto seguido no mesmo alvo dá +10% de dano (até 10×, zera ao trocar de alvo) | **Fogo-fátuo** (40 s): 9 chamas atacam o alvo atual, 2% do HP máx cada (chefe 1%) | +20% de dano contra chefe nas torres de Fogo |
| Água | Ataques cortam o escudo do alvo pela metade e anulam a regeneração | **Prisão d'Água** (45 s): prende o chefe por 3 s, e ele recebe +30% de dano enquanto está preso | Chefes entram com −8% de HP |
| Vento | Ataca 2 alvos (prioriza os de maior HP) | **Corte do Vento** (35 s): 5 golpes de 150% ATK + Quebra de DEF (−50% de armadura) por 6 s | +15% ATK em todas contra alvos com DEF quebrada |
| Luz | Dano verdadeiro (ignora armadura e escudo) | **Julgamento** (50 s): causa 15% do HP que falta no alvo | 10% do dano de todas as torres ignora armadura |
| Trevas | Ataques causam +3% do HP máx (chefe 1%) | **Eclipse** (50 s): marca o chefe por 6 s, e todo dano que ele recebe gera +30% de dano extra | +25% de dano contra inimigos abaixo de 30% HP |

## 9. Inimigos (MVP)

| Tipo | Característica |
|---|---|
| Comum | Base |
| Rápido | +60% de velocidade, −40% de HP |
| Blindado | Armadura de 40% |
| Escudeiro | Escudo de 30% do HP, que precisa ser quebrado antes do HP |
| Regenerador | Recupera 2% do HP/s |
| Elite | 5× HP, 1 habilidade (cura, escudo ou invocação) |
| Chefe | Elemento definido, com habilidades por fase |

- Armadura: `dano × (1 − armadura)`, com armadura máxima de 60%. A Quebra de DEF reduz a armadura pela metade.

## 10. Gacha

Invocar só gasta pedras, no Summonhenge (altar do hub). Cristais e mana compram pedras na loja.

| Pedra | Pool | Chances | Origem |
|---|---|---|---|
| Pedra de Invocação | Fogo/Água/Vento | 3★ 70% · 4★ 26% · 5★ 4% | Login diário, baús das runs, loja (100 cristais ou 1000 mana) |
| Pedra Lendária | Fogo/Água/Vento | 4★ 88% · 5★ 12% | Vitória no B5+, dia 7 do login, loja (700 cristais) |
| Pedra de Luz e Trevas | só Luz/Trevas | 4★ 85% · 5★ 15% | Vitória no B8+, loja (1200 cristais) |
| Pedra da Transcendência | qualquer elemento (Luz/Trevas com 1/3 do peso) | 5★ garantido | Primeira vitória no B10, loja (4000 cristais) |

- Pools por estrela: 3★ Pixie e Coruja (Fogo/Água/Vento); 4★ Dragãozinho e Tanuki (Fogo/Água/Vento) + Pixie e Coruja (Luz/Trevas); 5★ Kitsune (Fogo/Água/Vento) + Dragãozinho, Tanuki e Kitsune (Luz/Trevas).
- Torres de Luz/Trevas não saem das pedras normais e são mais fortes: +1 estrela natural e +25% de ATK base.
- Pity: 5★ garantido em 60 invocações (contando todas as pedras).
- Início: Pixie de Fogo grátis + 10 Pedras de Boas-vindas (rolam como a Pedra de Invocação).
- Valores de playtest.

## 11. Moedas e itens

| Item | Uso | Origem |
|---|---|---|
| Ouro | Colocar e subir tier na run (zera no fim) | Kills, renda por wave |
| Mana | Upgrade de runa, evolução, despertar | Runs, autofarm, venda de runa |
| Cristais | Comprar pedras (premium) | Robux, conquistas, primeira vitória por andar |
| Pedras de invocação (4 tipos, seção 10) | 1 invocação cada | Login diário, runs, loja |
| Essência (×5) + Arcana | Despertar | Runs ativas, conforme o elemento do dia |
| Fragmento Estelar | Evolução | Baús das runs ativas, cópias além do máximo |
| Poção de XP | Nível para torres no banco | Autofarm |
| Runa | Equipamento | Baús das runs, autofarm |

## 12. x1 DPS (fora do MVP, desenhado agora)

- Os dois jogadores jogam o mesmo andar em cópias do mapa lado a lado, com a mesma seed de waves e chamada livre de waves.
- Vence quem limpar primeiro, ou quem estiver na wave mais alta quando o tempo acabar.
- Ranqueado com runas reais (Pontos de Glória, ranking semanal = Arena). Casual com níveis normalizados.
- O leaderboard de tempo de limpeza por andar (que já existe no MVP) serve de semente da Arena.

## 13. Requisitos técnicos do MVP

1. Dano, drops e tempo de limpeza calculados no servidor. RNG com seed.
2. Status das torres, skills, runas e waves em tabelas de dados (ModuleScripts), não espalhados pelos scripts.
3. Relógio de simulação próprio, para o tempo de limpeza não depender da velocidade do jogo.
4. Medidor de dano por jogador (coop agora, x1 depois).
5. O autofarm é calculado pelos timestamps de entrada e saída do quadrado AFK, registrados pelo servidor, sem loop rodando por jogador. O progresso parcial da barra é salvo ao sair do quadrado.

## 14. Fora do MVP

Segundo despertar, modelos dedicados para as versões despertas, reapp/grind/gema de runa, estrela de runa, essências em três níveis, x1/Arena, voadores e invisíveis, mais mapas.

## 15. Monetização

- **Gamepasses:** velocidade 2x na run, slot extra de autofarm (farmar dois andares ao mesmo tempo no quadrado AFK), inventário de runas maior.
- **Dev products:** cristais.
