from django import template

register = template.Library()

@register.filter
def star_type(rating, star_number):
    """
    Returns '', '-half-o', or '-o' for Font Awesome 4 stars.
    Usage: {{ avg|star_type:1 }}
    """
    try:
        rating = float(rating or 0)
        star_number = int(star_number)
    except (TypeError, ValueError):
        return "-o"

    if rating >= star_number:
        return ""          # full star
    elif rating >= (star_number - 0.5):
        return "-half-o"   # half star
    return "-o"            # empty star


# =====================================

# from django import template

# register = template.Library()

# @register.filter
# def star_class(rating, position):
#     try:
#         rating = float(rating or 0)
#         position = int(position)
#     except (TypeError, ValueError):
#         return "fa-star-o"

#     if rating >= position:
#         return "fa-star"
#     elif rating >= (position - 0.5):
#         return "fa-star-half-o"
#     return "fa-star-o"

# ==============================
# from django import template

# register = template.Library()

# @register.filter
# def star_type(rating, position):
#     """
#     position: 1..5
#     returns: 'full' | 'half' | 'empty'
#     rating can be 0..5 (including .5)
#     """
#     try:
#         rating = float(rating)
#         position = int(position)
#     except (TypeError, ValueError):
#         return "empty"

#     if rating >= position:
#         return "full"
#     if rating >= (position - 0.5):
#         return "half"
#     return "empty"
