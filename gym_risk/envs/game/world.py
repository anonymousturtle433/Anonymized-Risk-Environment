CONNECT = {'Yellow_A': ['Yellow_B', 'Yellow_C', 'Yellow_D'],
                  'Yellow_B': ['Yellow_A', 'Yellow_C'],
                  'Yellow_C': ['Yellow_A', 'Yellow_B', 'Yellow_D', 'Blue_D'],
                  'Yellow_D': ['Yellow_A', 'Yellow_C', 'Green_A'],
                  'Blue_A': ['Yellow_C', 'Blue_D', 'Blue_B'],
                  'Blue_B': ['Blue_A', 'Blue_D', 'Blue_C'],
                  'Blue_C': ['Blue_D', 'Blue_B', 'Purple_A'],
                  'Blue_D': ['Blue_A', 'Blue_C', 'Blue_B'], 
                  'Purple_A': ['Purple_B', 'Purple_E', 'Green_E'],
                  'Purple_B': ['Purple_A', 'Purple_E', 'Purple_C', 'Purple_D'],
                  'Purple_C': ['Purple_D', 'Purple_B'],
                  'Purple_D': ['Purple_E', 'Purple_C', 'Purple_B'],
                  'Purple_E': ['Purple_A', 'Purple_B', 'Purple_D'],
                  'Green_A': ['Green_B'],
                  'Green_B': ['Green_A', 'Green_C', 'Green_D', 'Green_E'],
                  'Green_C': ['Green_B', 'Green_D'],
                  'Green_D': ['Green_C', 'Green_E', 'Green_B', 'Red_A'],
                  'Green_E': ['Green_B', 'Green_D', 'Purple_A'],
                  'Red_A': ['Green_D', 'Red_B', 'Red_C'],
                  'Red_B': ['Red_A', 'Red_C', 'Purple_E'],
                  'Red_C': ['Yellow_B', 'Blue_B', 'Red_A', 'Red_B']
}

AREAS = {
  "Yellow": (4, ["Yellow_A", "Yellow_B", "Yellow_C", "Yellow_D"]),
  "Blue": (4, ["Blue_B", "Blue_A", "Blue_C", "Blue_D"]),
  "Green": (5, ["Green_A", "Green_B", "Green_C", "Green_D", "Green_E"]),
  "Purple": (5, ["Purple_A", "Purple_B", "Purple_C", "Purple_D", "Purple_E"]),
  "Red": (3, ["Red_A", "Red_B", "Red_C"])
}

MAP = """
  bb              iijjkkk            
 bbbbbddd        iiijjjkkklll
aaaabcdddxxxxxxxxiiijjjkklll
 aaacccddd        iijjjjllll
 aaccc                mmmlll         nnn
   wv                  mmmmlBBBBBBBBBnnnppp
   wv                  mmmmCCCCCCCCCCnnnppp
   wv                  zA            oooppp                                      
   wv                  zA            oooppp
 eeeff             qqqqqq            oooppp    
 eeefff           qqqqqqrrDDDDDDDDDDDooo
 eegggffyyyyyyyyyyyqqqrrrr
  ggghhh            sssrrr 
   ghhhhh           sssstt    
     hhh            sssttt
                    uuttt
                    uuuu
                    uu
"""     


KEY = {
'b': "Yellow_A",
'a': "Yellow_B",
'c': "Yellow_C",
'd': "Yellow_D",
'e': "Blue_A",
'g': "Blue_B",
'h': "Blue_C",
'f': "Blue_D",
'i': "Green_A",
'j': "Green_B",
'k': "Green_C",
'l': "Green_D",
'm': "Green_E",
'n': "Red_A",
'o': "Red_B",
'p': "Red_C",
'q': "Purple_A",
's': "Purple_B",
'u': "Purple_C",
't': "Purple_D",
'r': "Purple_E",
'v': "ConnYB",
'w': "ConnBY",
'x': "ConnYG",
'y': "ConnBP",
'z': "ConnPG",
'A': "ConnGP",
'B': "ConnGR",
'C': "ConnRG",
'D': "ConnPR",
}

Action_map = {
0: "Yellow_A",
1: "Yellow_B",
2: "Yellow_C",
3: "Yellow_D",
4: "Blue_A",
5: "Blue_B",
6: "Blue_C",
7: "Blue_D",
8: "Green_A",
9: "Green_B",
10: "Green_C",
11: "Green_D",
12: "Green_E",
13: "Red_A",
14: "Red_B",
15: "Red_C",
16: "Purple_A",
17: "Purple_B",
18: "Purple_C",
19: "Purple_D",
20: "Purple_E"
}

Reversed_Action_map = {
"Yellow_A": 0,
"Yellow_B": 1,
"Yellow_C": 2,
"Yellow_D": 3,
"Blue_A": 4,
"Blue_B": 5,
"Blue_C": 6,
"Blue_D": 7,
"Green_A": 8,
"Green_B": 9,
"Green_C": 10,
"Green_D": 11,
"Green_E": 12,
"Red_A": 13,
"Red_B": 14,
"Red_C": 15,
"Purple_A": 16,
"Purple_B": 17,
"Purple_C": 18,
"Purple_D": 19,
"Purple_E":20
}