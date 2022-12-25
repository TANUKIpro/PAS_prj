"""
J8:
   3V3  (1) (2)  5V
 GPIO2  (3) (4)  5V
 GPIO3  (5) (6)  GND
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
   GND (25) (26) GPIO7
 GPIO0 (27) (28) GPIO1
 GPIO5 (29) (30) GND
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21
"""

VALVE_GPIO_LIST_L = [None]*6
VALVE_GPIO_LIST_R = [6, 13, 16, 5, 21, 20]

class Valve:
    class Right:
        class A:
            u = VALVE_GPIO_LIST_R[0]
            l = VALVE_GPIO_LIST_R[1]
        class B:
            u = VALVE_GPIO_LIST_R[2]
            l = VALVE_GPIO_LIST_R[3]
        class C:
            u = VALVE_GPIO_LIST_R[4]
            l = VALVE_GPIO_LIST_R[5]

    class Left:
        class A:
            u = VALVE_GPIO_LIST_L[0]
            l = VALVE_GPIO_LIST_L[1]
        class B:
            u = VALVE_GPIO_LIST_L[2]
            l = VALVE_GPIO_LIST_L[3]
        class C:
            u = VALVE_GPIO_LIST_L[4]
            l = VALVE_GPIO_LIST_L[5]
    
    class Emergency:
        class Switch:
            sw = None
        class Target:
            target_list = VALVE_GPIO_LIST_R + VALVE_GPIO_LIST_L

class Power:
    CPS = 12