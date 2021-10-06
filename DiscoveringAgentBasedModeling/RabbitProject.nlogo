breed [rabbits a-rabbit]
breed [cats cat]

rabbits-own [food_quota happy_time sad_time nb_sad nb_happy]
; food_quota         the food quantity the rabbit has eat (from 0 to 20)
; happy_time         elapsed time after having played with cat (from 0 to 6)
; sad_time           elapsed time after having fighted with cat (from 0 to 8)
; nb_sad             count the number of time where rabbit has been fighted by cats
; nb_happy           count the number of time where rabbit has played with cats

cats-own [territory time_outside time_inside animals friend happy_time sad_time]
; territory          the patches defining the cats territories
; time_outside       the time during which cat is outside its territory (after 3 ticks outside, cat will move to its territory again)
; time_inside        the time during which cat is inside its territory (after 5 ticks inside, cat will move outside its territory)
; animals            cats watch their surroundings
; friend             closest animal from the cat
; happy_time         elapsed time after having played with another animal (from 0 to 6)
; sad_time           elapsed time after having fighted with another animal (from 0 to 8)

patches-own [inside]
; inside             delimits the cats territories area (territory of cat n°i is marked with inside = i)

globals [r col_list cen_list ]
; r                  defines the radius of cats territories
; col_list           possible colours for cats
; cen_list           possible centers for cats territories



to Setup
  clear-all

  set r 4                                                    ; cat territory is a circle of radius r
  set col_list [4 24 84 104 134]                             ; 5 possible colours of cats
  set cen_list [[12 3] [5 9] [-6 12] [12 12] [12 -7]]        ; 5 possible centers of cats territories

  create-rabbits 1 [
    setxy (-1 + random 9) (1 + random 4)
    set shape "rabbit"
    set color white

    set food_quota 0
    set happy_time 0
    set sad_time 0
    set nb_happy 0
    set nb_sad 0
  ]


  create-cats cats_number
  [

    let cat_nb who                                             ; get the current number of the cat (cat_nb) inorder to chose its specific color / territory inside lists
    let cat_elt(cat_nb - 1)                                    ; rabbit has always the number 0, so cats have numbers from 1 to 5 but elements of lists are fom 0 to 4
    let col item cat_elt col_list                              ; colour of the current cat
    let cent item cat_elt cen_list                             ; current cat's territory center

    set shape "cat"
    set color col

    set territory patches-in-territory patch (item 0 cent) (item 1 cent)        ; create the cat territory (of radius r and center cent)
    ask territory
      [set pcolor (col + 4)                                    ; personalize the cat area
       set inside (cat_nb)                                     ; delimitation of its own territory
      ]
    move-to patch (item 0 cent) (item 1 cent)                  ; move the cat on the center of its territory

    set time_outside 0
    set time_inside 1
    set happy_time 0
    set sad_time 0
  ]

  setup-patches

  reset-ticks	

end


to setup-patches
  ask patches [
    if (pxcor > -2 and pxcor < 8) and (pycor > 0 and pycor < 5)[ ;rabbit enclosure
      set pcolor green
    ]
  ]
end


to Go
  ask rabbits [
    if (sad_time = 0)                                    ; if rabbit is still injured (= sad), then it no longer eats or moves
      [move-rabbits]
    rab-check-status                                     ; check status only, rabbit do not search interaction with other animals
  ]

  ask cats[
    move-cats
    cat-check-status                                     ; check status and verify whether cat wants to play, fight or do nothing with other animals ?
  ]

  tick
  if (ticks > 2000) [stop]

end

to move-rabbits

  ifelse(food_quota < 1)
    [eat_grass]                                          ; no more energy, rabbit needs to eat grass

    [ifelse (food_quota < 20)                            ; rabbits still hungry

      [ifelse (random 100 < rabbit_gluttony)             ; rabbits thinks about whether to move or not, according to its gluttony behavior
        [eat_grass]                                      ; don't want to move, rabbits is eating
        [move-to-enclosure]                              ; rabbit prefers moving
      ]
      [move-to-enclosure]                                ; no more hungry, rabbit moves
   ]

end

to move-to-enclosure

    right random 360                                     ; rabbit is moving
    forward 1

    if (xcor < -1)[set xcor -1]                          ; but still in its enclosure
    if (xcor > 7)[set xcor 7]
    if (ycor < 1)[set ycor 1]
    if (ycor > 4)[set ycor 4]

    set food_quota (food_quota - 1)                      ; moving removes -1 to food_quota

end

to eat_grass
  set food_quota  (food_quota  + 2)                      ; eating brings +2 to food_quota
end


to move-cats

  ifelse (random 100 < cats_adventurous)             ; if cat is adventurous: cat should moves

    [ifelse(time_outside < 3)                          ; not too many time outside
      [right random 360                                     ; cat moves because adventurous
       forward 5
       let cat_nb who                                       ; get the current number of the cat (cat_nb) inorder to chose its specific color / territory inside lists

       if ([inside] of patch-here = cat_nb)                 ; cat is inside its territory
          [right random 360                                 ; cat moves again because it is inside its territory, but must move outside
           forward (2 * r + 1)                              ; to be sure that this time cat is outside !
          ]

       ifelse(time_outside > 0)
          [set time_outside (time_outside + 1)]
          [set time_outside 1]
       set time_inside 0
      ]; end of cat moved outside

      [move-to one-of territory                        ; Too long time ouside (even if adventurous)
       ifelse (time_inside > 0)                             ; Cat moves inside its territory
         [set time_inside (time_inside + 1)]
         [set time_inside 1]
       set time_outside 0
      ]; end of cat moved inside

    ]; end of cat adventurous

    [move-to one-of territory                        ; cat moves inside its territory because not enough adventurous
     ifelse(time_inside < 5)                           ; not too many time inside
      [
       ifelse (time_inside > 0)                            ; cat remains inside its territory
         [set time_inside (time_inside + 1)]
         [set time_inside 1]
       set time_outside 0
      ]; end of cat moved inside

      [right random 360                                ; Too much time inside : cat moves outside (even if not very adventurous)
       forward (2 * r + 1)                                 ; to be sure that this time cat is outside (we previously moved the cat inside) !
       ifelse (time_outside > 0)
         [set time_outside (time_outside + 1)]
         [set time_outside 1]
       set time_inside 0
      ]; end of cat moved outside

    ]; end of cat NOT adventurous

end


to-report patches-in-territory [Center]

  let ptr []
  ask Center [                                                                ; creation of cats territories with the provided center and radius
    set ptr patches in-radius r
  ]

  report ptr

end

to rab-check-status

  if (sad_time = 0)                                                           ; if rabbit is not injured
    [if ((other cats-here = cats) and (food_quota > 0))                       ; if rabbit has moved toward a cat, it moved again
      [move-to-enclosure]
    ]

  if (happy_time > 0)                                                         ; rabbit already happy
    [ifelse (happy_time > 6)                                                  ; happy for a long enough time
      [set happy_time 0
       set shape "rabbit"
      ]
      [set happy_time (happy_time + 1)]
    ]

  if (sad_time > 0)                                                            ; rabbit already sad
    [ifelse (sad_time > 8)                                                     ; sad for a long enough time
      [set sad_time 0
       set shape "rabbit"
      ]
      [set sad_time (sad_time + 1)]
    ]


end


to cat-check-status

  if (happy_time > 0)                                                           ; cat already happy
    [ifelse (happy_time > 6)                                                    ; happy for a long enough time
      [set happy_time 0
       set shape "cat"
      ]
      [set happy_time (happy_time + 1)]
    ]

  if (sad_time > 0)                                                              ; cat already sad
    [ifelse (sad_time > 8)                                                       ; sad for a long enough time
      [set sad_time 0
       set shape "cat"
      ]
      [set sad_time (sad_time + 1)]
    ]

  view-other                                                                      ; cat is looking around

  if (any? animals)
    [ifelse ((random 100 < cats_playful) and (happy_time = 0) and (sad_time = 0)) ; the cat's playful behaviour is favoured : it is first verified whether cat wants to play
      [go-to-other "play"]                                                        ; cat is playful, and neither already happy nor sad, so ready to new encounters
      [if ((random 100 < cats_fighter) and (sad_time = 0) and (happy_time = 0))
        [go-to-other "fight"]                                                     ; cat is fighter, and neither already happy nor sad, so ready to new encounters
      ]
    ]; end of interaction with other animals

end

to view-other

  set animals (turtles in-radius 4) with [self != myself]                                 ; other animals are detected in the cat's field of vision

end

to go-to-other [verb]

  set friend min-one-of animals [distance myself]                                         ; detection of the closest animal is the cat's field of vision

  let id_friend 0
  let happy_friend 0
  let sad_friend 0
  let food_friend 0

  ask friend [                                                                             ; information on the friend's animal in order to know if it will escape
    set id_friend who
    set happy_friend happy_time
    set sad_friend sad_time

    if (id_friend = 0)                                                                    ; case where the neighbouring animal is the rabbit
      [set happy_friend 0                                                                 ; rabbit cannot avoid encouters with cats (because only inside its enclosure)
       set sad_friend 0                                                                   ; in that case the happy (resp sad) face of the rabbit can lasts less than 6 (resp 8) ticks
      ]
    ]

  if ((verb = "play") and (happy_friend = 0) and (sad_friend = 0))                        ; if other cat is already happy or sad, we consider that it avoids the encounter
      [move-to friend                                                                     ; cat approaches the other animal
        set shape "face happy"                                                            ; after having played with another animal, cat is happy during 6 ticks
        set happy_time 1
        ask friend [
          set shape "face happy"                                                          ; after having played with the current cat, the friend's animal is happy too, and also during 6 ticks
          set happy_time 1
          if (id_friend = 0)
            [set nb_happy (nb_happy + 1)                                                  ; we report the number of times where the rabbit (the friend's animal) has played with cats
             set sad_time 0                                                               ; the rabbit can not avoid cats, even if it was previously with sad face
            ]                                                                             ; if rabbit already had the happy face, then its previous counter is erased
        ]
      ]

  if ((verb = "fight") and (sad_friend = 0) and (happy_friend = 0))                        ; if other cat is already sad or happy, we consider that it avoids the encounter
      [move-to friend                                                                      ; cat approaches the other animal
       set shape "face sad"                                                                ; after having fighted with another animal, cat is sad during 8 ticks
       set sad_time 1
       ask friend [
          set shape "face sad"                                                             ; after having fighted with the current cat, the friend's animal is sad too, and also during 8 ticks
          set sad_time 1
          if (id_friend = 0)
            [set nb_sad (nb_sad + 1)                                                       ; we report the number of times where the rabbit (the friend's animal) has been fighted
             set happy_time 0                                                              ; the rabbit can not avoid cats, even if it was previously with happy face
            ]                                                                              ; if rabbit already had the sad face, then its previous counter is erased
        ]
      ]

end
@#$#@#$#@
GRAPHICS-WINDOW
9
69
446
507
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
47
21
242
54
1- Registration of parameters
Setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
284
22
392
55
2-Start / Stop
Go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

SLIDER
516
79
688
112
rabbit_gluttony
rabbit_gluttony
0
100
100.0
1
1
%
HORIZONTAL

PLOT
704
24
1317
174
food quota for the rabbit
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"default" 1.0 0 -15302303 true "" "plot [food_quota] of a-rabbit 0"

SLIDER
490
425
662
458
cats_number
cats_number
1
5
5.0
1
1
NIL
HORIZONTAL

SLIDER
706
424
878
457
cats_adventurous
cats_adventurous
0
100
50.0
1
1
%
HORIZONTAL

SLIDER
1158
423
1330
456
cats_fighter
cats_fighter
0
100
50.0
1
1
%
HORIZONTAL

SLIDER
927
423
1099
456
cats_playful
cats_playful
0
100
50.0
1
1
%
HORIZONTAL

MONITOR
572
218
843
331
Rabbit injured ?
[nb_sad] of a-rabbit 0
17
1
28

MONITOR
854
218
1187
331
Number of play with cats
[nb_happy] of a-rabbit 0
17
1
28

@#$#@#$#@
## WHAT IS IT?

This model tries to show the risks for a rabbit in relation to the cats in the neighbourhood.

There is only one rabbit, but up to 5 cats. 

Rabbit enclosure are the green patches. 

Cats territories are patches delimiting circles of different colours: territory and corresponding cat are of the same colour (but more or less dark).

## HOW IT WORKS

Rules for rabbit:
 - in case where rabbit is injured (still sad face), it no more eats / moves again until its wounds are healed (no more sad face)
 - it eats according to its gluttony behavior : if his stomach is not full, it could prefer eating
 - or it moves inside its enclosure, in case where it estimates that its stomach is full enough
 - if rabbit moves on the same patch than a cat, then the rabbit will go away in order to avoid cat. Rabbit does not seek interaction with other animals

Rules for cats:
 - it moves, according to its adventurous behaviour : it's a percentage which is 100% when cat always want to explore new areas
    -> but independently of its adventurous behavior, if the cat has been outside during a long time, it will always prefer to return to his territory
    -> and conversely, if the cats stayed on its territory for a long time, it will always perfer moving oustide
 - if another animal is detected, then cat could play, according to its playfil behavior
   -> the cat's playful behaviour is favoured : it is first verified whether cat wants to play 
   -> if the cat is already happy or sad, it will avoid the encounter
 - if another animal is detected, then cat could fight, according to its fighter behavior
   -> if the cat is already happy or sad, it will avoid the encounter

Rules for neighbourhood animal :
 - if the neighbouring animal is a cat which is already happy or sad, then it will avoid the encounter
 - il the neighbouring animal is the rabbit, then it cannot avoid the encounter because it remains in its enclosure

## HOW TO USE IT

Rabbit gluttony can be parametrized : it's a percentage which is 100% when rabbit only think about eating

There are 4 different parameters for the cat :
 - the number of cats can be chosen from 1 to 5
 - the advenurous behavior of the cat : it's a percentage which is 100% when cat wants to discover new areas
 - the playful behavior of the cat : it's a percentage which is 100% when cat always wants to play with other animals
 - the fighter behavior of the cat : it's a percentage which is 100% when cat always wants to fight with other animals

Reporting are only for rabbit :
 - the plot indicates the rabbit's satiety 
 - a monitor reports the number of time where the rabbit has been injured by cats
 - another monitor reports the number of time where the rabbit has played with cats

## THINGS TO NOTICE

After playing, the two animals involved become happy face.
 -> this happy face lasts during 6 ticks
After a fight, the two animals involved become sad face.
 -> this sad face lasts during 8 ticks

## THINGS TO TRY

User can try to modify the cats behaviors in order to understand how this results in injuries to the rabbit.

## EXTENDING THE MODEL

The cat's playful behaviour has been favoured, but other choices can be done. 

The gluttony of cats could be added, which will result in fewer chance to fight with rabbit, the cats could be busy eating rather than fighting. 

The model takes the assumption that the rabbit is not the master of its environment, it would rather suffer the events. On the contrary, cats do what they want. Those assumptions could be changed in order to give more power to the rabbit and less liberty to the cats. 

## NETLOGO FEATURES

## RELATED MODELS

## CREDITS AND REFERENCES
@#$#@#$#@
default
true
15
Polygon -7500403 true false 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

cat
false
0
Line -7500403 true 285 240 210 240
Line -7500403 true 195 300 165 255
Line -7500403 true 15 240 90 240
Line -7500403 true 285 285 195 240
Line -7500403 true 105 300 135 255
Line -16777216 false 150 270 150 285
Line -16777216 false 15 75 15 120
Polygon -7500403 true true 300 15 285 30 255 30 225 75 195 60 255 15
Polygon -7500403 true true 285 135 210 135 180 150 180 45 285 90
Polygon -7500403 true true 120 45 120 210 180 210 180 45
Polygon -7500403 true true 180 195 165 300 240 285 255 225 285 195
Polygon -7500403 true true 180 225 195 285 165 300 150 300 150 255 165 225
Polygon -7500403 true true 195 195 195 165 225 150 255 135 285 135 285 195
Polygon -7500403 true true 15 135 90 135 120 150 120 45 15 90
Polygon -7500403 true true 120 195 135 300 60 285 45 225 15 195
Polygon -7500403 true true 120 225 105 285 135 300 150 300 150 255 135 225
Polygon -7500403 true true 105 195 105 165 75 150 45 135 15 135 15 195
Polygon -7500403 true true 285 120 270 90 285 15 300 15
Line -7500403 true 15 285 105 240
Polygon -7500403 true true 15 120 30 90 15 15 0 15
Polygon -7500403 true true 0 15 15 30 45 30 75 75 105 60 45 15
Line -16777216 false 164 262 209 262
Line -16777216 false 223 231 208 261
Line -16777216 false 136 262 91 262
Line -16777216 false 77 231 92 261

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

rabbit
false
0
Polygon -7500403 true true 61 150 76 180 91 195 103 214 91 240 76 255 61 270 76 270 106 255 132 209 151 210 181 210 211 240 196 255 181 255 166 247 151 255 166 270 211 270 241 255 240 210 270 225 285 165 256 135 226 105 166 90 91 105
Polygon -7500403 true true 75 164 94 104 70 82 45 89 19 104 4 149 19 164 37 162 59 153
Polygon -7500403 true true 64 98 96 87 138 26 130 15 97 36 54 86
Polygon -7500403 true true 49 89 57 47 78 4 89 20 70 88
Circle -16777216 true false 37 103 16
Line -16777216 false 44 150 104 150
Line -16777216 false 39 158 84 175
Line -16777216 false 29 159 57 195
Polygon -5825686 true false 0 150 15 165 15 150
Polygon -5825686 true false 76 90 97 47 130 32
Line -16777216 false 180 210 165 180
Line -16777216 false 165 180 180 165
Line -16777216 false 180 165 225 165
Line -16777216 false 180 210 210 240

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.2.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
