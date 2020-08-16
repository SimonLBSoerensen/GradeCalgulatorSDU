from bs4 import BeautifulSoup
import pyperclip
import numpy as np
from datetime import datetime
from prettytable import PrettyTable
import uuid

debug_mode = False

decimals = 1
bar_length = 50


def cal_GPA(grads, ects, low_grade=2, high_grade=12):
    total_ects = np.sum(ects)
    prodoct_score = np.sum(grads * ects)
    return (prodoct_score / total_ects - low_grade) / (high_grade - low_grade) * 10 + 2


def number_grade_test(grade):
    number_grade = False
    try:
        grade = int(grade)
    except:
        pass
    else:
        number_grade = True
    return number_grade

def dtimearr_to_str(ar, format="%d-%m-%Y"):
    return [d.strftime(format) for d in ar]

file_name = "grades" + ".txt"
def file_writer(*args):
    with open(file_name, "a") as f:
        for arg in args:
            f.write(str(arg))
        f.write("\n")


bachelor = []
master = []

sdu_mode = input("Are you from SDU? (y/n): ").lower() == "y"
file_on = input("Write result to file? (y/r/n) (r for y+random filename): ").lower()
if file_on == "r":
    file_name = str(uuid.uuid4()) + ".txt"
    file_on = "y"
file_on = file_on == "y"

if sdu_mode:
    if debug_mode:
        with open("example.html") as f:
            html = f.read()
    else:
        _ = input("Copi the html of the 'Grade Results' page on 'selvbprod.sdu.dk' to you clipboard and hit enter...")
        html = pyperclip.paste()

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find(id="resultTableGrup")

    if debug_mode:
        bch_date = datetime.strptime("25-06-2019", "%d-%m-%Y")  #

    else:
        bch_fomat = input(
            "Enter a day there is between the last bachelor grade and (before) the first master grade (dd-mm-yyyy): ")
        bch_date = datetime.strptime(bch_fomat, "%d-%m-%Y")

    for tr in table.find_all("tr")[1:]:
        code, name, judged, registered, grade, letter_grade, ects = [td.get_text().strip() for td in tr.find_all("td")]

        ects = float(ects)
        judged = datetime.strptime(judged, "%d.%m.%Y")
        registered = datetime.strptime(registered, "%d.%m.%Y")

        number_grade = number_grade_test(grade)
        if number_grade:
            grade = int(grade)

        if ects == 0:
            continue

        arr = [code, name, judged, registered, grade, letter_grade, ects, number_grade]

        if judged <= bch_date:
            bachelor.append(arr)
        else:
            master.append(arr)
else:
    for level, arr in zip(["bachelor", "master"], [bachelor, master]):
        while True:
            temp = input(
                "{}: Input a course (or 'x' for end of {} courcses). Enter 'ECTS,grade', grade can be numeric or B for pass: ".format(
                    level.title(), level))
            if temp == "x":
                break

            ects, grade = temp.split(",")

            ects = float(ects)

            number_grade = number_grade_test(grade)
            if number_grade:
                grade = int(grade)

            arr.append([None, None, None, None, grade, None, ects, number_grade])

bachelor = np.array(bachelor)
master = np.array(master)


def print_part_info(part_name, part_data, receiver_function=print):
    bar_padding = bar_length - len(part_name)
    receiver_function(part_name + "-" * bar_padding)

    if len(part_data) == 0:
        return

    codes, names, judgeds, registereds, grades, letter_grades, ects, number_grade = part_data.T

    receiver_function("Number of courses:", len(grades))

    receiver_function("ECTS sum:", np.round(np.sum(ects), decimals=decimals))

    number_grads_idxs = np.where(number_grade == 1)[0]
    passed_npassed_idx = np.delete(np.arange(len(number_grade)), number_grads_idxs)
    receiver_function("Grade stats (mean +- stddev / min / max): {:0.2f} +- {:0.2f} / {:0.2f} / {:0.2f}".format(
        np.mean(grades[number_grads_idxs]),
        np.std(grades[number_grads_idxs]),
        np.min(grades[number_grads_idxs]),
        np.max(grades[number_grads_idxs])))
    receiver_function("Number/passed grade ECTS: {:0.1f}/{:0.1f}".format(np.sum(ects[number_grads_idxs]),
                                                                         np.sum(ects[passed_npassed_idx])))
    receiver_function("Percentage of passed/not passed courses (based on ECTS): {:0.2f}%".format(
        np.sum(ects[passed_npassed_idx]) / np.sum(ects) * 100))

    number_dict = dict(np.array(np.unique(grades[number_grads_idxs], return_counts=True)).T)
    letter_dict = dict(np.array(np.unique(grades[passed_npassed_idx], return_counts=True)).T)
    receiver_function("Grads counts:", {**letter_dict, **number_dict})

    m_gpa = cal_GPA(grades[number_grads_idxs], ects[number_grads_idxs])
    receiver_function("GPA:", np.round(m_gpa, decimals=decimals))

    table = PrettyTable()

    sort_idxs = np.argsort(judgeds)

    codes = np.array(codes)[sort_idxs]
    names = np.array(names)[sort_idxs]
    judgeds = np.array(judgeds)[sort_idxs]
    judgeds_str = dtimearr_to_str(judgeds)
    registereds = np.array(registereds)[sort_idxs]
    registereds_str = dtimearr_to_str(registereds)
    grades = np.array(grades)[sort_idxs]
    letter_grades = np.array(letter_grades)[sort_idxs]
    ects = np.array(ects)[sort_idxs]

    field_names = ["Code", "Name of Course", "Graded", "Released", "Grade", "ECTS-Gr.", "ECTS"]
    for i, d in enumerate([codes, names, judgeds_str, registereds_str, grades, letter_grades, ects]):

        table.add_column(field_names[i], d)
    receiver_function(table)
    receiver_function("")


print_part_info("Bachelor", bachelor)
print_part_info("Master", master)
print_part_info("Overall", np.array(list(bachelor) + list(master)))

if file_on:
    print_part_info("Bachelor", bachelor, file_writer)
    print_part_info("Master", master, file_writer)
    print_part_info("Overall", np.array(list(bachelor) + list(master)), file_writer)
input("Exit...")
