def two(sad):
    if sad == 0:
        return 1
    return (1 + two(sad-1)**2)%26


threearr = [1, 6, 11, 22, 19, 16, 5, 10, 21, 20, 13, 0]


def three(sad):
    return threearr[sad%12]
    # if sad == 0:
    #     return 1
    # return (two(sad)**2 + 2*three(sad-1))%26


# for i in range(100):
#     print(three(i))

x = ""
x = x + chr(three(139064) + 65)
x = x + chr(three(635457) + 65)
x = x + chr(three(650399) + 65)
x = x + chr(three(650399) + 65)
x = x + chr(three(1032151) + 65)
x = x + chr(three(1217717) + 65)
x = x + chr(three(1917304) + 65)
x = x + chr(three(2224106) + 65)
x = x + chr(three(2336593) + 65)
x = x + chr(three(2369909) + 65)
x = x + chr(three(2397934) + 65)
x = x + chr(three(2504802) + 65)
x = x + chr(three(2504802) + 65)
x = x + chr(three(2511217) + 65)
x = x + chr(three(2622792) + 65)
x = x + chr(three(2634860) + 65)
x = x + chr(three(2735913) + 65)
x = x + chr(three(2739168) + 65)
x = x + chr(three(2895494) + 65)
x = x + chr(three(3009243) + 65)
x = x + chr(three(3038083) + 65)
x = x + chr(three(3152860) + 65)
x = x + chr(three(3430894) + 65)
x = x + chr(three(3539943) + 65)

print(x)
