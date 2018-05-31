
outer = 4
inner = 3
# arr = [ [0] * inner ] * outer
arr = [[0] * inner for _ in range(outer)]

print('>>> Assigning values ...')
for i in range(0, outer):
    for j in range(0, inner):
        arr[i][j] = i * j
    print('i = {}: {}'.format(i, arr[i]))

print('\n>>> After assignment ...')
for i in range(0, outer):
    print('i = {}: {}'.format(i, arr[i]))