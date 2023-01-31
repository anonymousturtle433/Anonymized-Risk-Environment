#Colors
BLACK = (0, 0 ,0)
WHITE = (255, 255, 255)
LIGHT_RED = (0, 51, 51)
GREY = (204, 204, 204)
LIGHT_GREY = (234, 234, 234)
GREEN = (0, 179, 160)
LIGHT_GREEN = (0, 230, 77)
YELLOW = (230, 230, 0)
LIGHT_YELLOW = (255, 255, 26)
BLUE = (0, 0 , 255)
RED = (0, 204, 0)
OCEAN_BLUE = (0, 119, 190)
YELLOW = (196, 193, 0)
SOUTH_AMERICA = (219, 135, 0)
AFRICA = (160,160,160)
EUROPE = (142,148,255)
ASIA = (142,226,169)
OCEANIA = (195,127,255)

#PLAYERS
PINK = (255,132,203)
TEAL = (0,128,128)
ORANGE = (255, 135, 0)

# set up pixel coordinates for territories
Yellow_A = [(105,146),(121,115),(164,115),(182,80),(227,80),(243,114),(288,114),(304,146),(287,182),(304,218),(288,254),(247,254),
			(227,218),(247,182),(229,146),(182,146),(164,179), (121,179)]
Yellow_A = {"Name":"Yellow_A", "Coordinates":Yellow_A, "Color":YELLOW, "Bubble":(185, 95), "Country":"A", "Country_Coordinates":(126,158)}


Yellow_B = [(121,182), (165,182), (184,148), (227,148), (243, 182), (226, 217), (243,252), (226,284), (180,284), (164,317),
			(118,317), (103,284), (121,249), (106,215)]
Yellow_B = {"Name":"Yellow_B", "Coordinates":Yellow_B, "Color":YELLOW, "Bubble":(160, 205), "Country":"B","Country_Coordinates":(126,298) }


Yellow_C = [(167,319), (184,288), (230,288), (244,259), (290,259), (303,288), (288,322), (303,358),
			(288,391), (244,391), (227,353), (183,353)]
Yellow_C = {"Name":"Yellow_C", "Coordinates":Yellow_C, "Color":YELLOW, "Bubble":(220, 300), "Country":"C","Country_Coordinates":(191,335)}


Yellow_D = [(308,355), (293,322), (308, 287), (294,255), (309,223), (352,223), (367,255), (352,287), (367,322), (352, 355)]
Yellow_D = {"Name":"Yellow_D", "Coordinates":Yellow_D, "Color":YELLOW, "Bubble":(311, 270), "Country":"D","Country_Coordinates":(318,335)}


Blue_A = [(123,549), (138,516), (183,516), (198,482), (243, 482), (256,513), (243, 546), (198, 546), (182,580), (138,580)]
Blue_A = {"Name":"Blue_A", "Coordinates":Blue_A, "Color":SOUTH_AMERICA, "Bubble":(145, 525),  "Country":"A", "Country_Coordinates":(228,525)}


Blue_B = [(185,583), (200,550), (245,550), (260,583), (305,583), (320,616), (305, 649), (260, 649), (243, 684), (199, 684),
		  (185, 650), (200,616)]
Blue_B = {"Name":"Blue_B", "Coordinates":Blue_B, "Color":SOUTH_AMERICA, "Bubble":(228, 595), "Country":"B", "Country_Coordinates":(200,665)}


Blue_C = [(246, 687), (261, 655), (307, 655), (324, 621), (367, 621), (382, 655), (429, 655), (444, 686), (429, 717), (382,717),
		  (367,752), (322, 752), (305,786), (261, 786), (248,753), (262,718)]
Blue_C = {"Name":"Blue_C", "Coordinates":Blue_C, "Color":SOUTH_AMERICA, "Bubble":(310, 670), "Country":"C", "Country_Coordinates":(265,770)}

Blue_D = [(249,547), (263,514), (307,514), (321,549), (367,549), (381,581), (367,613), (323,613), (307,579), (263, 579)]
Blue_D = {"Name":"Blue_D", "Coordinates":Blue_D, "Color":SOUTH_AMERICA, "Bubble":(265, 525), "Country":"D", "Country_Coordinates":(350,595)}





Purple_A = [(616, 519), (631, 487), (677, 487), (694, 453), (736, 453), (752, 487), (799, 487), (814, 518), (799, 549),
			(752, 549), (737, 584), (692, 584), (675, 618), (631, 618), (618, 585), (632, 550)]
Purple_A = {"Name":"Purple_A", "Coordinates":Purple_A, "Color":AFRICA, "Bubble":(680, 505), "Country":"A", "Country_Coordinates":(635,600)}


Purple_B = [(680, 622), (695, 589), (740, 589), (755, 622), (800, 622), (815, 655), (800, 688), (755, 688), (738, 723),
			(694, 723), (680, 689), (695, 655)]
Purple_B = {"Name":"Purple_B", "Coordinates":Purple_B, "Color":AFRICA, "Bubble":(717, 635), "Country":"B", "Country_Coordinates":(695,705)}


Purple_E = [(744, 583), (757, 553), (804, 553), (818, 520), (864, 520), (877, 549), (862, 583), (877, 619), (862, 652),
			(818, 652), (801, 616), (757, 616)]
Purple_E = {"Name":"Purple_E", "Coordinates":Purple_E, "Color":AFRICA, "Bubble":(800, 567), "Country":"E", "Country_Coordinates":(760,595)}


Purple_D = [(759, 691), (803, 691), (822, 657), (865, 657), (881, 691), (864, 726), (881, 761), (864, 793), (818, 793),
			(802, 826), (756, 826), (741, 793), (759, 758), (744, 724)]
Purple_D = {"Name":"Purple_D", "Coordinates":Purple_D, "Color":AFRICA, "Bubble":(794, 720),  "Country":"D", "Country_Coordinates":(765,805)}


Purple_C = [(693, 860), (678, 827), (693, 792), (679, 760), (694, 728), (737, 728), (752, 760), (737, 792), (752, 827), (737, 860)]
Purple_C = {"Name":"Purple_C", "Coordinates":Purple_C, "Color":AFRICA, "Bubble":(697, 750), "Country":"C", "Country_Coordinates":(695,835)}

Green_A = [(482, 213), (499, 182), (545, 182), (559, 153), (605, 153), (618, 182), (603, 216), (618, 252), (603, 285), (559, 285),
		  (542, 247), (498, 247)]
Green_A = {"Name":"Green_A", "Coordinates":Green_A, "Color":EUROPE, "Bubble":(522, 194), "Country":"A", "Country_Coordinates":(500,230)}


Green_B = [(623, 251), (608, 218), (623, 183), (609, 151), (624, 119), (667, 119), (682, 151), (667, 183), (682, 218), (667, 251),
		   (684, 289), (727, 289), (743, 320), (727, 352), (685, 352), (670, 318), (623, 318), (609, 285)]
Green_B = {"Name":"Green_B", "Coordinates":Green_B, "Color":EUROPE, "Bubble":(627, 268),  "Country":"B", "Country_Coordinates":(690,335)}


Green_C = [(673, 183), (688, 150), (733, 150), (748, 183), (793, 183), (808, 216), (793, 249), (748, 249),
		   (731, 284), (687, 284), (673, 250), (688, 216)]
Green_C = {"Name":"Green_C", "Coordinates":Green_C, "Color":EUROPE, "Bubble":(714, 196), "Country":"C", "Country_Coordinates":(680,245)}


Green_D = [(749, 253), (796, 253), (811, 214), (797, 182), (812, 150), (855, 150), (870, 182), (855, 214), (870, 249),
		   (855, 282), (870, 316), (855, 349), (811, 349), (797, 316), (749, 316), (735, 282)]

Green_D = {"Name":"Green_D", "Coordinates":Green_D, "Color":EUROPE, "Bubble":(791, 263), "Country":"D", "Country_Coordinates":(820,160)}


Green_E = [(735, 355), (749, 322), (793, 322), (807, 357), (853, 357), (867, 389), (853, 421),
		   (809, 421), (793, 387), (749, 387)]
Green_E = {"Name":"Green_E", "Coordinates":Green_E, "Color":EUROPE, "Bubble":(756, 337),  "Country":"E", "Country_Coordinates":(748,370)}


Red_A = [(1014, 467), (999, 434), (1014, 399), (1000, 367), (1015, 335), (1058, 335), (1073, 367), (1058, 399), (1073, 434), (1058, 467)]
Red_A = {"Name":"Red_A", "Coordinates":Red_A, "Color":OCEANIA, "Bubble":(1017, 368), "Country":"A", "Country_Coordinates":(1020,450)}


Red_B = [(1014, 603), (999, 570), (1014, 535), (1000, 503), (1015, 471), (1058, 471), (1073, 503), (1058, 535), (1073, 570), (1058, 603),
		 (1073,637), (1058, 670), (1014, 670), (1000, 637)]
Red_B = {"Name":"Red_B", "Coordinates":Red_B, "Color":OCEANIA, "Bubble":(1017, 550), "Country":"B", "Country_Coordinates":(1015,655)}


Red_C = [(1078, 503), (1063, 470), (1078, 435), (1064, 403), (1079, 371), (1122, 371), (1137, 403), (1122, 435), (1137, 470),
		 (1122, 503), (1137, 537), (1122, 570), (1138, 603), (1122, 640), (1079, 640), (1063, 603), (1079, 570), (1064, 537)]
Red_C = {"Name":"Red_C", "Coordinates":Red_C, "Color":OCEANIA, "Bubble":(1081, 458), "Country":"C", "Country_Coordinates":(1080,620)}

TERRITORIES = [Yellow_A, Yellow_B, Yellow_C, Yellow_D, Blue_A, Blue_B, Blue_C, Blue_D, Purple_A,
				Purple_B, Purple_C, Purple_D, Purple_E, Green_A, Green_B, Green_C, Green_D, Green_E, Red_A, Red_B, Red_C]
