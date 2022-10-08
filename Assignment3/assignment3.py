# ----------------------------------------------------
# Assignment 3
# CMPUT 291
# Section: B1
# Name: Yi Yang
# CCID: yyang13
# Student ID: 1542688
# Collaborator: No one
# ----------------------------------------------------


import sqlite3


def getAction():
    '''
    This function prompts user to enter a desire command, the function iterates until a correct action is entered.
    '''

    actions = ['1', '2', '3', '4', '5']
    action = str(input('\nPlease select an option by entering a number: \n' + '1. Find accepted papers\n' +
                   '2. FInd papers assigned for review\n' + '3. Find papers with inconsistent reviews\n' +
                    '4. Find papers according to difference score\n' + '5. Exit\nOption: '))
    while action not in actions:
        action = str(input('Sorry, invalid entry. Please enter a choice from 1 to 5.\nOption: '))
    else:
        return action


def task1(connection, cursor):
    '''
    This function performs queries for task 1
    '''

    # Prompt user to enter an area
    inputArea = str(input("Please enter an area code: ")).upper()

    # Check if entered area is valid, if not, querying will not be performed
    checkArea = '''
    SELECT name
    FROM areas
    WHERE name = "%s"
    ''' % inputArea
    cursor.execute(checkArea)
    checkResult = cursor.fetchall()
    if len(checkResult) == 0:
        print("Invalid area code")
    else:
        # Querying all the accepted papers in the given area. The results will be grouped by the average overall score
        # in descending order
        getTitleAndAvg = '''
        SELECT P.title, AVG(R.overall)
        FROM papers P, reviews R
        WHERE P.decision = "A"
        AND P.area = "%s"
        AND P.id = R.paper
        GROUP BY R.paper
        ORDER BY AVG(R.overall) DESC
        ''' % (inputArea)
        cursor.execute(getTitleAndAvg)
        connection.commit()

        # Print out the results
        result = cursor.fetchall()
        if len(result) == 0:
            print("No results.")
        else:
            if len(result) == 1:
                print("Accepted Paper in the area %s: " % (inputArea))
            else:
                print("Accepted Papers in the area %s: " % (inputArea))
            for i in range(0, len(result)):
                print("\nPaper Title: " + str(result[i][0]) + "\nAvg Overall Scores: " + str(round(result[i][1], 1)))
    print("-" * 40)

    return


def task2(connection, cursor):
    '''
    This function performs queries for task 2
    '''

    # Prompt user to enter an user email
    inputEmail = str(input("Please enter an user email: "))

    # Check if entered email is valid
    checkEmail = '''
       SELECT DISTINCT email
       FROM users
       WHERE email like "%s"
       ''' % inputEmail
    cursor.execute(checkEmail)
    checkResult = cursor.fetchall()
    if len(checkResult) == 0:
        print("Invalid entered user email")
    else:
        # Querying reviewed paper with the given user email
        getTitle = '''
        SELECT P.title
        FROM papers P, reviews R
        WHERE P.id = R.paper
        AND R.reviewer like "%s"
        ORDER BY P.id
        ''' % (inputEmail)
        cursor.execute(getTitle)
        connection.commit()

        # Print out the results
        result = cursor.fetchall()
        if len(result) == 0:
            print("No paper has been assigned to this reviewer")
        else:
            if len(result) == 1:
                print("\nAssigned Paper Title: ")
            else:
                print("\nAssigned Paper Titles: ")
            for i in range(0, len(result)):
                print(" "*5 + str(result[i][0]))
    print("-" * 40)

    return


def task3(connection, cursor):
    '''
    This function performs queries for task 3
    '''

    # Prompt user to enter a number as the percentage
    try:
        percentage = abs(float(input("Enter a number as %: ")))
        upper = round((1 + percentage / 100), 2)
        lower = round((1 - percentage / 100), 2)
    except Exception:
        exit("Invalid input")

    # Get average overall score of all reviewed papers
    getTitleAndAvg = '''
            SELECT paper, AVG(overall)
            FROM reviews
            GROUP BY paper
            '''
    cursor.execute(getTitleAndAvg)
    result = []
    paperAvg = cursor.fetchall()

    # Get all papers that have at least one inconsistent reviews
    for i in range(0, len(paperAvg)):
        getIdAndTitle = '''
                SELECT id, title
                FROM papers
                WHERE id in
                    (SELECT DISTINCT paper
                    FROM reviews
                    WHERE paper = %d
                    and (overall > %f or overall < %f))
                ''' % (int(paperAvg[i][0]), round(float(paperAvg[i][1] * upper), 2), round(float(paperAvg[i][1] * lower), 2))

        cursor.execute(getIdAndTitle)
        result.append(cursor.fetchall())
    connection.commit()

    # Print out the results
    if len(result) == 0:
        print("No paper has inconsistent reviews.")
    else:
        print("\nPapers that have at least one inconsistent reviews: ")
        for i in range(0, len(result)):
            if len(result[i]) != 0:
                print("\nPaper id:", result[i][0][0], "\nPaper Title:", result[i][0][1])
    print("-" * 40)

    return

def createView(connection, cursor):
    # Get the average of overall score in each area
    getAreaAndAvg = '''
    CREATE VIEW avgOfArea (area, AVG)
    AS  SELECT p.area, AVG(R.overall)
        FROM papers P, reviews R
        WHERE P.id = R.paper
        GROUP BY P.area
    '''

    # Get the average of overall score of each paper
    getPaperAndAvg = '''
    CREATE VIEW avgOfPaper (area, id, title, AVG)
    AS  SELECT P.area, P.id, P.title, AVG(R.overall)
        FROM papers P, reviews R
        WHERE P.id = R.paper
        GROUP BY R.paper
    '''

    # Create a view that contains three columns: paper id, paper title and the difference
    createDiffScore = '''
    CREATE VIEW DiffScore (pid, ptitle, difference)
    AS  SELECT P.id, P.title, round(abs(P.AVG - A.AVG), 2)
        FROM avgOfPaper P, avgOfArea A
        WHERE P.area = A.area
    '''
    cursor.execute(getAreaAndAvg)
    cursor.execute(getPaperAndAvg)
    cursor.execute(createDiffScore)
    connection.commit()

    return


def dropView(connection, cursor):
    # Drop the views
    cursor.execute('''
        DROP VIEW IF EXISTS avgOfArea;
        ''')
    cursor.execute('''
        DROP VIEW IF EXISTS avgOfPaper;
        ''')
    cursor.execute('''
        DROP VIEW IF EXISTS DiffScore;
        ''')
    connection.commit()

    return


def task4(connection, cursor):
    '''
    This function performs queries for task 4
    '''

    # Prompt user to enter lower bound and upper bound numbers
    try:
        lower = abs(float(input("Enter a positive lower bound number: ")))
        upper = abs(float(input("Enter a positive upper bound number: ")))
    except Exception:
        exit("Invalid inputs")

    # Get the email and name of the reviewers who have reviewed a paper with difference between a given range
    getEmailAndName = '''
    SELECT email, name
    FROM users
    WHERE email in
    (SELECT DISTINCT R.reviewer
    FROM reviews R, DiffScore D
    WHERE R.paper = D.pid
    AND %f <= D.difference
    AND D.difference <= %f
    )''' % (lower, upper)
    cursor.execute(getEmailAndName)
    connection.commit()

    # Print out the results
    result = cursor.fetchall()
    if len(result) == 0:
        print("\nNo one has review a paper that is in range from %.2f to %.2f" % (lower, upper))
    else:
        if len(result) == 1:
            print("\nReviewer who has reviewed a paper with a difference between %.2f and %.2f: " % (lower, upper))
        else:
            print("\nReviewers who have reviewed a paper with a difference between %.2f and %.2f: " % (lower, upper))
        for i in range(0, len(result)):
            print("\nEmail Address:", result[i][0], "\nName:", result[i][1])


    print("-" * 40)

    return


def main():
    # Create connection to the database
    connection = sqlite3.connect('./A3.db')
    cursor = connection.cursor()
    dropView(connection, cursor)
    createView(connection, cursor)

    quit = False

    while not quit:
        action = getAction()
        if action == '1':
            task1(connection, cursor)
        elif action == '2':
            task2(connection, cursor)
        elif action == '3':
            task3(connection, cursor)
        elif action == '4':
            task4(connection, cursor)
        elif action == '5':
            quit = True

    print('Exiting the system')

    connection.commit()
    connection.close()
    return


if __name__ == "__main__":
    main()

