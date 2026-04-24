import ckanext.cuprit.logic.auth_utils as auth_utils
import ckan.plugins.toolkit as tk
import re
from ckan import logic


def is_organization_admin(user_id, organization_id):
    """
    Checks if the specified user is an admin of the specified organization.

    Args:
        user_id (str): The user ID to check.
        organization_id (str): The organization ID to check against.

    Returns:
        bool: True if the user is an admin of the organization, False otherwise.
    """
    context = {'user': user_id}
    try:
        # Attempt to check if the user can update the organization
        logic.check_access('organization_update', context, {'id': organization_id})
        return True
    except logic.NotAuthorized:
        return False
    except Exception as e:
        # Log or handle the exception as needed
        print('Error checking organization admin status: {}'.format(str(e)))
        return False



def is_editor(user: str, office: str =None) -> bool:
    """
    Returns True if user is editor of given organisation.
    If office param is not provided checks if user is editor of any organisation

    :param user: user name
    :param office: office id
    """
    return auth_utils.is_editor({'user': user}, {'user': user}, office)

def get_recent_articles() -> dict:
    """
    get recent updated packages for startpage
    """
    result = tk.get_action("package_search")({}, {"rows": 10, "sort": "metadata_modified desc"})
    return result["results"]

def format_orcid(authors: str) -> str:
    """
    Link author to ORCIDs and RORIDs if IDs are found, combining them within parentheses.
    Additionally, extracts and formats plain text inside curly braces.
    """
    authors_list = authors_to_list(authors)
    author_html_str = ""
    for author in authors_list:
        author_name = author.get('name', '')
        author_type = author.get('type', None)
        author_orcid = author.get('orcid', None)
        author_rorid = author.get('rorid', None)
        links = []
        if author_type:
            links.append(f'<span class="tag opacity-75">{author_type}</span>')
        if author_orcid:
            links.append(f'<a href="https://orcid.org/{author_orcid}" class="tag opacity-75" target="_blank">ORCID ID: {author_orcid}</a>')
        if author_rorid:
            links.append(f'<a href="https://ror.org/{author_rorid}" class="tag opacity-75" target="_blank">ROR ID: {author_rorid}</a>')

        # Combine ORCID, RORID, and type with a space if all or some exist
        combined_links = ' '.join(links)
        
        # Append combined links to the author name if not empty
        if combined_links:
            author_with_links = f'{author_name} {combined_links}'
        else:
            author_with_links = author_name

        author_html_str += f'{author_with_links}<br>'
    
    return author_html_str

def authors_to_list(authors: str) -> list:
    """
    Return a list of authors or contributors as dicts.
    """
    authors = authors.split(";")
    authors_dicts = []
    for author in authors:
        author_dict = {}
        author_orcid = re.search('(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', author)
        author_rorid = re.search('\[(.*?)\]', author)
        author_type = re.search('\{(.*?)\}', author) # Search for text within curly brackets

        author_dict['orcid'] = author_orcid.group() if author_orcid else None
        author_dict['rorid'] = author_rorid.group(1) if author_rorid else None
        author_dict['type'] = author_type.group(1) if author_type else None

        # Clean author name from identifiers
        clean_author = author.replace('(' + author_dict['orcid'] + ')', '').strip() if author_orcid else author
        clean_author = clean_author.replace('[' + author_dict['rorid'] + ']', '').strip() if author_rorid else clean_author
        clean_author = clean_author.replace('{' + author_dict['type'] + '}', '').strip() if author_type else clean_author
        author_dict['name'] = clean_author

        authors_dicts.append(author_dict)

    return authors_dicts

def format_resources(resources: str) -> str:
    resources = str(resources)
    resources = resources.replace('"','')
    re.sub('"', '', resources)
    resources_html_str = ''
    resources = resources.split(";")
    for resource in resources:
        resources_html_str += f'{resource}<br>'
    return resources_html_str