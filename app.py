company = input('Введите место работы: ')
try:
    age_from = int(input('Введите начальный возраст: '))
    age_to = int(input('Введите конечный возраст: '))
except ValueError:
    print('Возраст - число, а не буквы и символы')
    exit()

if not company:
    print('Не введено название компании')
    exit()

link = 'https://vk.com/search?c%5Bage_from%5D={age_from}&c%5Bage_to%5D={age_to}&c%5Bbmonth%5D={month}&c%5B{company}%5D=агенство&c%5Bname%5D=1&c%5Bper_page%5D=40&c%5Bphoto%5D={photo}&c%5Bsection%5D=people&c%5Bsex%5D={sex}'

links = []
for age in range(age_from, age_to+1):
    for month in range(1, 13):
        for sex in 0, 1:
            for photo in 0, 1:
                links.append(link.format(company=company, age_from=age, age_to=age, month=month, photo=photo, sex=sex))

print(f'total: {len(links)}')

with open('result.txt', 'w') as file:
    file.write('\n'.join(links))
