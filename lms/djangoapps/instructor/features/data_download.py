"""
Define steps for instructor dashboard - data download tab
acceptance tests.
"""

#pylint: disable=C0111
#pylint: disable=W0621

from lettuce import world, step
from nose.tools import assert_in, assert_regexp_matches  # pylint: disable=E0611
from terrain.steps import reload_the_page

from courseware.tests.factories import StaffFactory, InstructorFactory


def go_to_section(section_name):
    # section name should be one of
    # course_info, membership, student_admin, data_download, analytics
    world.visit('/courses/edx/999/Test_Course')
    world.css_click('a[href="/courses/edx/999/Test_Course/instructor"]')
    world.css_click('div.beta-button-wrapper>a')
    world.css_click('a[data-section="{0}"]'.format(section_name))


@step(u'I click "([^"]*)"')
def click_a_button(step, button):  # pylint: disable=unused-argument
    # Go to the data download section of the instructor dash
    go_to_section("data_download")

    if button == "Generate Grade Report":
        # Click generate grade report button
        world.css_click('input[name="calculate-grades-csv"]')

        # Expect to see a message that grade report is being generated
        expected_msg = "Your grade report is being generated! You can view the status of the generation task in the 'Pending Instructor Tasks' section."
        world.wait_for_visible('#grade-request-response')
        assert_in(
            expected_msg, world.css_text('#grade-request-response'),
            msg="Could not find grade report generation success message."
        )

    elif button == "Grading Configuration":
        world.css_click('input[name="dump-gradeconf"]')

    elif button == "List enrolled students' profile information":
        world.css_click('input[name="list-profiles"]')


@step(u'I see a table of student profiles')
def find_student_profile_table(step):  # pylint: disable=unused-argument
    print 'inside find_student_profile_talbe'
    # Find the grading configuration display
    world.wait_for_visible('#data-student-profiles-table')
    if world.role == 'instructor':
        expected_data = [
            world.instructor.username,
            world.instructor.email,
            world.instructor.profile.name,
            world.instructor.profile.gender,
            world.instructor.profile.goals
        ]
    elif world.role == 'staff':
        expected_data = [
            world.staff.username,
            world.staff.email,
            world.staff.profile.name,
            world.staff.profile.gender,
            world.staff.profile.goals
        ]
    for datum in expected_data:
        if datum not in world.css_text('#data-student-profiles-table'):
            print datum
        assert_in(datum, world.css_text('#data-student-profiles-table'))


@step(u"I see the grading configuration for the course")
def find_grading_config(step):  # pylint: disable=unused-argument
    # Find the grading configuration display
    world.wait_for_visible('#data-grade-config-text')
    # expected config is the default grading configuration from common/lib/xmodule/xmodule/course_module.py
    expected_config = u"""-----------------------------------------------------------------------------
Course grader:
<class 'xmodule.graders.WeightedSubsectionsGrader'>

Graded sections:
  subgrader=<class 'xmodule.graders.AssignmentFormatGrader'>, type=Homework, category=Homework, weight=0.15
  subgrader=<class 'xmodule.graders.AssignmentFormatGrader'>, type=Lab, category=Lab, weight=0.15
  subgrader=<class 'xmodule.graders.AssignmentFormatGrader'>, type=Midterm Exam, category=Midterm Exam, weight=0.3
  subgrader=<class 'xmodule.graders.AssignmentFormatGrader'>, type=Final Exam, category=Final Exam, weight=0.4
-----------------------------------------------------------------------------
Listing grading context for course edx/999/Test_Course
graded sections:
[]
all descriptors:
length=0"""
    assert_in(expected_config, world.css_text('#data-grade-config-text'))



@step(u"I see a csv file in the grade reports table")
def find_grade_report_csv_link(step):  # pylint: disable=unused-argument
    # Need to reload the page to see the grades download table
    reload_the_page(step)
    world.wait_for_visible('#grade-downloads-table')
    # Find table and assert a .csv file is present
    expected_file_regexp = 'edx_999_Test_Course_grade_report_\d{4}-\d{2}-\d{2}-\d{4}\.csv'
    assert_regexp_matches(
        world.css_html('#grade-downloads-table'), expected_file_regexp,
        msg="Expected grade report filename was not found."
    )


@step(u'Given I am "([^"]*)" for a course')
def i_am_an_instructor(step, role):  # pylint: disable=unused-argument
    # Store the role
    assert_in(role, ['instructor', 'staff'])

    # Clear existing courses to avoid conflicts
    world.clear_courses()

    # Create a new course
    course = world.CourseFactory.create(
        org='edx',
        number='999',
        display_name='Test Course'
    )

    world.course_id = 'edx/999/Test_Course'
    world.role = 'instructor'
    # Log in as the an instructor or staff for the course
    if role == 'instructor':
        # Make & register an instructor for the course
        world.instructor = InstructorFactory(course=course.location)
        world.enroll_user(world.instructor, world.course_id)

        world.log_in(
            username=world.instructor.username,
            password='test',
            email=world.instructor.email,
            name=world.instructor.profile.name
        )
    else:
        world.role = 'staff'
        # Make & register a staff member
        world.staff = StaffFactory(course=course.location)
        world.enroll_user(world.staff, world.course_id)

        world.log_in(
            username=world.staff.username,
            password='test',
            email=world.staff.email,
            name=world.staff.profile.name
        )
