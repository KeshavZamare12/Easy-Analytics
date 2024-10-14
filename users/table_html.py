
def generate_table_html(dataframe):
    """Generates HTML for a Bootstrap-styled table from a DataFrame."""
    table_html = '<table id="footer-search" class="table table-striped table-bordered nowrap table-info overflow-auto">'
    table_html += '<thead><tr><th class="text-center bg-info"> Index</th>'
    
    # Adding header
    for column in dataframe.columns:
        table_html += f'<th class="text-center bg-info">{column}</th>'
    table_html += '</tr></thead><tbody>'

    # Adding rows
    for index, row in dataframe.iterrows():
        table_html += '<tr>'
        table_html += f'<td class="text-center">{index}</td>'
        for value in row:
            table_html += f'<td class="text-center">{value}</td>'
        table_html += '</tr>'

    table_html += '</tbody><tfoot><tr><th class="text-center">Index</th>'
    for column in dataframe.columns:
        table_html += f'<th class="text-center">{column}</th>'
    table_html += '</tr></tfoot><table>'
    return table_html

from django.core.paginator import Paginator
def generate_table_html2(dataframe, entries=10, page=1, sort_column=None, sort_order='asc', search_term=''):
    paginator = Paginator(dataframe.values.tolist(), entries,)
    page_obj = paginator.get_page(page)

    # Start building the HTML
    table_html = '<div class="mb-3">'
    table_html += '<div class="row">'
    
    # Dropdown for entries per page
    table_html += '''
        <div class="col-sm-4 float-start d-flex justify-content-start">
            <label for="entries" class="pe-2">Show</label>
            <select id="entries" class="form-select pe-2" onchange="window.location.href='?entries=' + this.value + '&page=1&search={search_term}';">
                <option value="10" {'selected' if entries == 10 else ''}>10</option>
                <option value="25" {'selected' if entries == 25 else ''}>25</option>
                <option value="50" {'selected' if entries == 50 else ''}>50</option>
                <option value="100" {'selected' if entries == 100 else ''}>100</option>
            </select>
            <label for="entries" class=" ps-2 pe-2">entries</label>
        </div>
    '''

    # Search input
    table_html += f'''<div class="col-sm-8">
    <form method="get" class="d-flex ps-2">
        <div class="col-sm-4">
        </div>
        <input type="text" name="search" class="form-control pe-2" value="{search_term}" placeholder="Search...">
        <button type="submit" class="btn btn-primary ms-2">Search</button>
    </form>
    </div>
    '''
    
    table_html += '</div></div>'

        # Table structure
    table_html = '<form id="searchForm" method="get">'
    table_html += '<table class="table table-striped table-bordered nowrap table-info overflow-auto">'
    table_html += '<thead><tr><th class="text-center bg-info">Index</th>'

    # Adding header
    for column in dataframe.columns:
        sort_order_link = 'asc' if sort_order == 'desc' else 'desc'
        table_html += (
            f'<th class="text-center bg-info">{column}'
            f'<a href="?sort_column={column}&sort_order=asc&entries={entries}&page={page}&search={search_term}" class="text-decoration-none"><span class="ps-2"><i class="fas fa-arrow-up pe-2"></i></a>'
            f'<a href="?sort_column={column}&sort_order=desc&entries={entries}&page={page}&search={search_term}" class="text-decoration-none"><i class="fas fa-arrow-down"></i></a></span></th>'
        )

    table_html += '</tr><tr>'
    table_html += '<th class="text-center"><input type="text" name="search_index" class="form-control" placeholder="Search Index" oninput="autoSubmit()"></th>'

    for column in dataframe.columns:
        table_html += (
            f'<th class="text-center">'
            f'<input type="text" name="search_{column}" class="form-control" placeholder="Search {column}" oninput="autoSubmit()"/>'
            '</th>'
        )

    table_html += '</tr>'
    table_html += '</thead><tbody>'

    # Adding rows for the current page
    for idx, row in enumerate(page_obj):
        table_html += '<tr>'
        table_html += f'<td class="text-center">{(page - 1) * entries + idx + 1}</td>'  # Calculate the index for display, adjusted for human-friendly indexing
        for value in row:
            table_html += f'<td class="text-center">{value}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table></form>'

    # Pagination controls
    table_html += '<nav aria-label="Page navigation">'
    table_html += '<div class="row d-flex justify-content-between mb-2">'
    table_html += f'<div class="col-sm-4">Showing {(page - 1) * entries} - {min(page * entries, paginator.count)} of {paginator.count} entries</div>'
    table_html += '<div class="col-sm-8 float-end" ><ul class="pagination justify-content-center">'

    # First and Previous
    if page_obj.has_previous():
        table_html += f'<li class="page-item"><a class="page-link" href="?page=1&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">First</a></li>'
        table_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Previous</a></li>'

    # Calculate page range to show only 10 pages at a time
    start_page = max(1, page - 5)  # Start 5 pages before the current page
    end_page = min(paginator.num_pages, start_page + 9)  # Show up to 10 pages

    if end_page - start_page < 9:  # Adjust if there are fewer than 10 pages to show
        start_page = max(1, end_page - 9)

    # Page numbers
    for i in range(start_page, end_page + 1):
        if i == page:
            table_html += f'<li class="page-item active" aria-current="page"><span class="page-link">{i}</span></li>'
        else:
            table_html += f'<li class="page-item"><a class="page-link" href="?page={i}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">{i}</a></li>'

    # Next and Last
    if page_obj.has_next():
        table_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Next</a></li>'
        table_html += f'<li class="page-item"><a class="page-link" href="?page={paginator.num_pages}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Last</a></li>'

    table_html += '</ul></div></div></nav>'

    return table_html

def generate_table_html2(dataframe, entries=10, page=1, sort_column=None, sort_order='asc', search_term=''):
    paginator = Paginator(dataframe.values.tolist(), entries)
    page_obj = paginator.get_page(page)

    # Start building the HTML
    table_html = '<div class="mb-3">'
    table_html += '<div class="row">'

    # Dropdown for entries per page
    table_html += '''
        <div class="col-sm-4 float-start d-flex justify-content-start">
            <label for="entries" class="pe-2">Show</label>
            <select id="entries" class="form-select pe-2" onchange="window.location.href='?entries=' + this.value + '&page=1&search={search_term}';">
                <option value="10" {'selected' if entries == 10 else ''}>10</option>
                <option value="25" {'selected' if entries == 25 else ''}>25</option>
                <option value="50" {'selected' if entries == 50 else ''}>50</option>
                <option value="100" {'selected' if entries == 100 else ''}>100</option>
            </select>
            <label for="entries" class=" ps-2 pe-2">entries</label>
        </div>
    '''

    # Search input
    table_html += f'''<div class="col-sm-8">
    <form method="get" class="d-flex ps-2">
        <div class="col-sm-4">
        </div>
        <input type="text" name="search" class="form-control pe-2" value="{search_term}" placeholder="Search...">
        <button type="submit" class="btn btn-primary ms-2">Search</button>
    </form>
    </div>
    '''
    
    table_html += '</div></div>'

    # Table structure
    table_html += '<form id="searchForm" method="get">'
    table_html += '<table class="table table-striped table-bordered nowrap table-info overflow-auto">'
    table_html += '<thead><tr><th class="text-center bg-info">Index</th>'

    # Adding header with sorting
    for column in dataframe.columns:
        sort_order_link = 'asc' if sort_order == 'desc' else 'desc'
        table_html += (
            f'<th class="text-center bg-info">{column}'
            f'<a href="?sort_column={column}&sort_order=asc&entries={entries}&page={page}&search={search_term}" class="text-decoration-none"><span class="ps-2"><i class="fas fa-arrow-up pe-2"></i></a>'
            f'<a href="?sort_column={column}&sort_order=desc&entries={entries}&page={page}&search={search_term}" class="text-decoration-none"><i class="fas fa-arrow-down"></i></a></span></th>'
        )

    table_html += '</tr><tr>'
    table_html += '<th class="text-center"><input type="text" name="search_index" class="form-control" placeholder="Search Index" oninput="autoSubmit()"></th>'

    for column in dataframe.columns:
        table_html += (
            f'<th class="text-center">'
            f'<input type="text" name="search_{column}" class="form-control" placeholder="Search {column}" oninput="autoSubmit()"/>'
            '</th>'
        )

    table_html += '</tr>'
    table_html += '</thead><tbody>'

    # Adding rows for the current page
    for idx, row in enumerate(page_obj):
        table_html += '<tr>'
        table_html += f'<td class="text-center">{(page - 1) * entries + idx + 1}</td>'  # Calculate the index for display
        for value in row:
            table_html += f'<td class="text-center">{value}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table></form>'

    # Pagination controls
    table_html += '<nav aria-label="Page navigation">'
    table_html += '<div class="row d-flex justify-content-between mb-2">'
    table_html += f'<div class="col-sm-4">Showing {(page - 1) * entries} - {min(page * entries, paginator.count)} of {paginator.count} entries</div>'
    table_html += '<div class="col-sm-8 float-end"><ul class="pagination justify-content-center">'

    # First and Previous
    if page_obj.has_previous():
        table_html += f'<li class="page-item"><a class="page-link" href="?page=1&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">First</a></li>'
        table_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Previous</a></li>'

    # Calculate page range to show only 10 pages at a time
    start_page = max(1, page - 5)  # Start 5 pages before the current page
    end_page = min(paginator.num_pages, start_page + 9)  # Show up to 10 pages

    if end_page - start_page < 9:  # Adjust if there are fewer than 10 pages to show
        start_page = max(1, end_page - 9)

    # Page numbers
    for i in range(start_page, end_page + 1):
        if i == page:
            table_html += f'<li class="page-item active" aria-current="page"><span class="page-link">{i}</span></li>'
        else:
            table_html += f'<li class="page-item"><a class="page-link" href="?page={i}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">{i}</a></li>'

    # Next and Last
    if page_obj.has_next():
        table_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Next</a></li>'
        table_html += f'<li class="page-item"><a class="page-link" href="?page={paginator.num_pages}&entries={entries}&search={search_term}&sort_column={sort_column}&sort_order={sort_order}">Last</a></li>'

    table_html += '</ul></div></div></nav>'

    return table_html

