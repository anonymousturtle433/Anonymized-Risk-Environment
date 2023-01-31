#structure: dictionary(keys - map number)-> value dictionary(keys - player color) ->
# tuple of lists(territories to draft and reinforcement amounts (tuple of territory and amount))
#reinforcement amount = total number of troops on the map on that territory 
MAP_PLACEMENTS = {'A':{'grey':{'Yellow_B':4, 'Yellow_C':5, "Red_A":1, "Red_B":2, "Red_C":2},
                       'black':{"Blue_A":3, "Blue_B":3, "Purple_A":5, "Purple_B":1, "Green_E":2},},

                  'B':{'grey':{"Yellow_A":1, "Yellow_D":2, "Green_A":5, "Blue_D":3, "Blue_C":3}, 
                       'black':{"Yellow_C":4, "Blue_A":2, "Green_D":3, "Purple_C":4, "Purple_E":1}},

                  'C':{'grey':{"Yellow_A":4, "Yellow_B":2, "Green_C":1, "Green_D":4, "Green_E":3}, 
                       'black':{"Yellow_C":1, "Yellow_D":1, "Blue_B":5, "Red_A":5, "Purple_E":2}},

                  'D':{'grey':{"Blue_C":2, "Green_A":4, "Purple_A":5, "Red_B":3}, 
                       'black':{"Yellow_B":2, "Yellow_C":3, "Red_C":3, "Purple_C":1, "Purple_D":1, "Purple_E":4}},

                  'E':{'grey':{"Green_A":5, "Green_B":1, "Green_C":2, "Green_D":2, "Green_E":4}, 
                       'black':{"Yellow_D":5, "Purple_A":5, "Red_A":4}},

                  'F':{'grey':{'Blue_A': 3, 'Blue_B':1, 'Purple_E':4, 'Red_B': 4, 'Red_C': 2},
                       'black':{'Blue_C':2, 'Green_A':3, 'Green_D':3, 'Purple_C':1, 'Purple_D':3, 'Red_A':2}},

                  'G':{'grey':{"Green_C":4, "Green_D":4, "Green_E":4, "Purple_A":2, "Red_A":1}, #this map has 15 grey troops
                       'black':{"Yellow_C":1, "Yellow_D":3, "Blue_D":2, "Green_A":2, "Green_B":6}},

                  'H':{'grey':{"Yellow_B":5, "Yellow_C":1, "Yellow_D":2, "Green_C":3, "Blue_A":3}, 
                       'black':{"Yellow_A":1, "Blue_C":2, "Red_C":4, "Purple_B":2, "Purple_C":1, "Purple_E":4}},

                  'I':{'grey':{"Blue_B":1, "Blue_D":2, "Green_A":3, "Green_E":4, "Purple_A":4 }, 
                       'black':{"Yellow_B":5, "Yellow_D":2, "Green_B":4, "Purple_D":3}},

                  'J':{'grey':{"Blue_A":1, "Blue_B":1, "Green_C":4, "Green_D":4, "Red_A":4}, 
                       'black':{"Yellow_A":2, "Yellow_C":4, "Blue_C":2, "Blue_D":2, "Red_B":4}},

                  'K':{'grey':{"Yellow_B":1, "Blue_B":8, "Blue_C":2, "Green_E":2, "Red_B":1}, 
                       'black':{"Purple_A":7, "Purple_B":1, "Purple_E":6}},

                  'L':{'grey':{"Yellow_A":7, "Yellow_D":2, "Green_B":1, "Green_C":1, "Blue_C":1, "Purple_C":1, "Purple_D":1}, 
                       'black':{"Green_A":6, "Purple_A":5, "Red_A":2, "Red_C":1}},

                  'M':{'grey':{"Yellow_B":5, "Yellow_C":4, "Yellow_D":1, "Purple_B":2, "Purple_C":2}, 
                       'black':{"Blue_A":3, "Blue_B":4, "Blue_D":2, "Green_D":5}},

                  'N':{'grey':{"Blue_A":6, "Green_C":4, "Green_E":4}, #original only had 5 troops in blue a for, 13 grey troops total
                       'black':{"Yellow_A":1, "Blue_C":2, "Green_A":2, "Purple_C":1, "Purple_E":4, "Red_C":4}},

                  'O':{'grey':{"Red_B":7, "Red_C":7}, 
                       'black':{"Yellow_A":1, "Yellow_D":2,"Blue_C":2, "Green_D":6, "Purple_B":1, "Red_A":2}}
                  }

#NOT ACTUAL HUMAN DATA.
HUMAN_SELECTIONS = {'A':{0:{"Blue_C":1, "Green_B":1, "Yellow_A":2, "Purple_C":2, "Purple_D":3, "Purple_E":3, "Blue_D":2},
                         1:{"Green_C":14},
                         2:{"Green_D":6, "Blue_D":8}},
                    'B':{0:{"Red_A":4, "Red_B":6, "Red_C":4},
                         1:{"Red_A":7, "Red_C":7, "Red_B":2},
                         2:{"Red_A":2, "Red_B":4, "Red_C":2, "Blue_B":6}},
                    'C':{0:{"Red_B":4, "Purple_B":6, "Red_C":4},
                         1:{"Purple_B":6, "Red_C":8},
                         2:{"Purple_A":2, "Purple_B":1, "Purple_C":1, "Purple_D":1, "Green_A":4, "Green_B":4, "Blue_A":1}},
                    'D':{0:{"Blue_A":4, "Blue_D":4, "Green_E":3, "Green_D":3},
                         1:{"Green_B":2, "Blue_A":3, "Purple_B":4, "Yellow_A":2, "Red_A":3},
                         2:{"Red_A":4, "Purple_B":6, "Blue_B":2, "Yellow_A":2}},
                    'E':{0:{"Blue_C":3, "Blue_A":4, "Blue_B":4, "Blue_D":3},
                         1:{"Purple_E":6, "Red_B":8},
                         2:{"Blue_A":2, "Blue_B":4, "Blue_C":3, "Blue_D":3, "Yellow_A":2}},
                    'F':{0:{"Yellow_B":5, "Yellow_C":4, "Yellow_D":4, "Yellow_A":1},
                         1:{"Yellow_C":4, "Yellow_D":6, "Green_C":4},
                         2:{"Yellow_A":1, "Yellow_B":5, "Yellow_C":4, "Yellow_D":4}},
                    'G':{0:{"Blue_A":4, "Blue_B":5, "Purple_C":5},
                         1:{"Blue_C":2, "Blue_B": 4, "Blue_A":3 , "Yellow_B":2, "Yellow_A":3},
                         2:{"Red_B":2, "Red_C":4, "Yellow_A":4, "Yellow_B":4}},
                    'H':{0:{"Green_A":3, "Green_B":5, "Green_D":3, "Green_E":3},
                         1:{"Red_B":6, "Red_A":8},
                         2:{"Blue_D":3, "Blue_B":4, "Red_A":3, "Red_B":4}},
                    'I':{0:{"Blue_A":2, "Red_B":4, "Red_C":3, "Purple_E":5},
                         1:{"Blue_A":4, "Red_A":6, "Red_B":4},
                         2:{"Red_A":1, "Red_B":2, "Red_C":1, "Blue_A":3, "Blue_C":3, "Purple_C":4}},
                    'J':{0:{"Green_B":3, "Green_E":5, "Yellow_D":3, "Yellow_B":3},
                         1:{"Red_C":4, "Yellow_B":6, "Yellow_D":4},
                         2:{"Red_C":3, "Green_B":5, "Green_E":4, "Green_A":2}},
                    'K':{0:{"Green_A":2, "Blue_A":4, "Red_A":3, "Purple_C":3, "Green_B":2},
                         1:{"Red_A":6, "Red_C":8},
                         2:{"Yellow_A":3, "Yellow_D":5, "Red_C":6}},
                    'L':{0:{"Blue_A":4, "Blue_B":6, "Blue_D":4},
                         1:{"Purple_E":2, "Purple_B":3, "Blue_B":3, "Green_E":2, "Red_B":4},
                         2:{"Blue_A":3, "Blue_B":9, "Blue_D":2}},
                    'M':{0:{"Red_A":4, "Red_B":2, "Red_C":1, "Blue_C":7},
                         1:{"Red_A":4, "Purple_E":4, "Purple_D":2, "Red_B":1, "Green_E":2, "Green_C":1},
                         2:{"Red_A":4, "Red_B":4, "Green_E":3, "Green_B":3}},
                    'N':{0:{"Yellow_C":5, "Yellow_D":5, "Purple_A":4},
                         1:{"Yellow_C":7, "Yellow_B":4, "Yellow_D":3},
                         2:{"Red_B":6, "Red_A":8}},
                    'O':{0:{"Yellow_C":6, "Green_C":8},
                         1:{"Yellow_B":3, "Yellow_C":3, "Blue_A":2, "Blue_B":2, "Blue_D":4},
                         2:{"Green_A":2, "Green_B":2, "Green_C":2, "Green_E":2, "Yellow_B":3, "Yellow_C":3}},
                    }