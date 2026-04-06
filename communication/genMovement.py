from .stdoutParser import Execute_and_Parse
# f = open('filemap.txt', 'r')
# numberOfVertex, numberOfEdges = map(int, f.readline().split())
# print(numberOfVertex, numberOfEdges, sep = ", ")
# for line in f.readlines():
#     print(line, end = '')
# f.close()

dir_map = {'north': 0, 'east': 1, 'south': 2, 'west': 3}
def commute():

    Vertexs, Paths = Execute_and_Parse(dir_map)

    Placement = [j[0] for i in Paths for j in i]
    Movement = [j[1] for i in Paths for j in i]

    #print(Movement)

    return Placement, Movement

if __name__ == "__main__":
    commute()