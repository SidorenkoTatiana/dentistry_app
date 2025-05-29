from .pages.login import login_page
from .pages.dashboard import dashboard_page
from .pages.registration import registration_page
from .pages.schedule import schedule_page
from .pages.patient import patient_page
from .pages.service import service_page
from .pages.doctor import doctor_page
from .pages.profile import profile_page

PAGES = {
    "login": login_page,
    "dashboard": dashboard_page,
    "registration": registration_page,
    "schedule": schedule_page,
    "patient": patient_page,
    "service": service_page,
    "doctor": doctor_page,
    "profile": profile_page
}
