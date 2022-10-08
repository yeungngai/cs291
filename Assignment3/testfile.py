import sqlite3


connection = sqlite3.connect('./A3.db')
cursor = connection.cursor()

inputArea = input("Enter the area: ")

query1 = '''
SELECT *
FROM papers
WHERE area = "%s"
''' % (inputArea)


cursor.execute(query1)
connection.commit()

print(type(cursor))


# rows = cursor.fetchall()
#
# if len(rows) == 0:
#     print("No results found.")
# else:
#     for i in range(0, len(rows)):
#         print(rows[i])



