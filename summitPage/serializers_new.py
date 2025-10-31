from .utils import get_category_name_from_id
# registration/serializers.py
def serialize_registrant(registrant):
    """Return a safe dictionary representation of a registrant."""
    return {
        "title": registrant.title,
        "first_name": registrant.first_name,
        "other_names": registrant.second_name,
        "email": registrant.email,
        "phone": registrant.phone,
        "organization_type": registrant.organization_type,
        "organization": registrant.other_organization_type,
        "job_title": registrant.job_title,
        "category": get_category_name_from_id(registrant.category),
        "registration_date": registrant.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
