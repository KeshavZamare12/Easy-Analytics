# users/views.py
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .forms import UserRegistrationForm,UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from .models import User,Profile
from django.contrib.auth import logout
import os,mimetypes
import pandas as pd
import json,csv,io,mpld3,re
import matplotlib
import plotly.express as px
matplotlib.use('Agg') 
from .forms import UploadFileForm
import matplotlib.pyplot as plt
from .table_html import generate_table_html,generate_table_html2
from .data_analyze import Stat_Methods,Descriptive
from .mask_data import mask_data_method
from django.core.paginator import Paginator


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'users/login.html')
def index(request):
    return render(request, "users/base.html")

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def view_profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return redirect('edit_profile')  # Redirect to edit profile if no profile exists

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'users/view_profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        # Optionally create a new profile or handle the error
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
             # Update user information if necessary
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            return redirect('view_profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mobile_no': profile.mobile_no,
            'profile_pic': profile.profile_pic,
        }
        form = UserProfileForm(initial=initial_data)

    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def home(request):
    user = request.user
    profile = user.profile
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, "users/home.html",context)
def extract_value_after_last_dot(string):
    last_dot_index = string.rfind('.')
    return string[last_dot_index + 1:]
    
def upload_file(request):
    data = None
    form = UploadFileForm()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_type = form.cleaned_data['file_type']
            uploaded_file = request.FILES['file']
            # Check if the uploaded file's MIME type matches the expected type
            if extract_value_after_last_dot(str(uploaded_file)) != file_type:
                form.add_error('file', f"The uploaded file must be of type {file_type}.")
            else:
            # Read the file based on its type
                try:
                    if file_type == 'csv':
                        data = pd.read_csv(uploaded_file)
                    elif file_type == 'json':
                        json_data = json.load(uploaded_file)
                        key_name = form.cleaned_data.get('key_name')
                        # Check if a key name was provided
                        if key_name and key_name in json_data:
                            data = pd.json_normalize(json_data[key_name])
                        else:
                            # Assume the JSON is a list of records
                            data = pd.json_normalize(json_data)
                    elif file_type == 'xlsx':
                        sheet_name = form.cleaned_data.get('sheet_name')
                        data = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                    # Store the DataFrame in the session
                    request.session['uploaded_data'] = data.to_dict(orient='records')  
                except Exception as e:
                    form.add_error(None, f"Error processing file: {e}")

    if data is not None and not data.empty:
        data_html = data.to_html(classes='table table-striped table-bordered  table-warning ')
        data_html= data_html.replace('<th>', '<th class="text-center">')
        return render(request, 'fileupload/upload.html', {'form': form, 'data': data_html})

    return render(request, 'fileupload/upload.html', {'form': form})


def modify_data_view(request):
    if 'uploaded_data' not in request.session:
        count1=True
        return render(request, 'fileupload/modify_data.html', {
            'count1': count1,
        })
    # Retrieve the DataFrame from the session
    uploaded_data_dict = request.session['uploaded_data']
    df = pd.DataFrame.from_dict(uploaded_data_dict)
    numerical_col=df.select_dtypes(include=['number']).columns
    categorical_col=df.select_dtypes(include=['object']).columns
    modified_data = None
    columns = df.columns.tolist()
    count=0
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_columns = request.POST.getlist('selected_columns')
        if action == 'drop_null_rows':
            threshold = len(df.columns) * 0.5
            if selected_columns:
                df.dropna(subset=selected_columns, axis=0,inplace=True)
            elif threshold > 0:
                df.dropna(thresh=threshold,inplace=True)
        elif action == 'fill_data':
            fill_method=request.POST.get("fillingMethod")
            if fill_method =='mean':
                for column in selected_columns:
                    if column in categorical_col:
                        continue
                    else:
                        df[column].fillna(df[column].mean(),inplace=True)
            elif fill_method =="median":
                for column in selected_columns:
                    df[column].fillna(df[column].median(),inplace=True)
            elif fill_method =='mode':
                for column in selected_columns:
                    df[column].fillna(df[column].mode()[0],inplace=True)
            else:                
                fill_value = request.POST.get('fillingValue')
                for column in selected_columns:
                    df[column].fillna(fill_value, inplace=True)
        elif action == 'replace_value':
            old_value = request.POST.get('old_value')
            new_value = request.POST.get('new_value')
            for column in selected_columns:
                df[column].replace(old_value, new_value, inplace=True)
        elif action == 'change_dtype':
            new_dtype = request.POST.get('new_dtype')
            for column in selected_columns:
                if df[column].dtype == new_dtype:
                    continue
                elif new_dtype == "date":
                    df[column] = pd.to_datetime(df[column])
                df[column] = df[column].astype(new_dtype)
        elif action == 'drop_duplicates':
            df.drop_duplicates(inplace=True)
        elif action == 'drop_col':
            df.drop(selected_columns,axis=1,inplace=True)
        elif action == 'mapping':
            col1 = request.POST.get('column1')
            col2 = request.POST.get('column2')
            df[col1] = df[col1].fillna(df[col2])
            #df[col1].fillna(df.groupby(col2)[col1].transform('first'), inplace=True)
        elif action=="null_count":
            check_data=Stat_Methods(df).null_count()
            count+=1
        elif action=="see_null_data":
            check_data=Stat_Methods(df).see_null_data()
            count+=1
        elif action =="mask_data":
            input_pattern=request.POST.get("pattern_val")
            modified_data=mask_data_method(df,selected_columns,input_pattern)
        if count==1:
            return render(request,'fileupload/modify_data.html',{
                'columns':columns,
                'modified_data':generate_table_html(check_data),
            })
        request.session['uploaded_data'] = df.to_dict(orient='records')
        modified_data = generate_table_html(df)
        return render(request, 'fileupload/modify_data.html', {
            'columns': columns,
            'modified_data': modified_data,
        })
    else:
        return render(request,'fileupload/modify_data.html', {
            'columns': columns,
            'modified_data': generate_table_html(df),
        })

def analyze_data_view(request):
    if 'uploaded_data' not in request.session:
        count1=True
        return render(request, 'fileupload/modify_data.html', {
            'count1': count1,
        })

    # Retrieve the DataFrame from the session
    uploaded_data_dict = request.session['uploaded_data']
    df = pd.DataFrame.from_dict(uploaded_data_dict)
    numerical_col=df.select_dtypes(include=['number']).columns
    categorical_col=df.select_dtypes(include=['object']).columns
    data_analysis_types = [
    "Descriptive Analysis",
    "Diagnostic Analysis",
    "Predictive Analysis",
    "Prescriptive Analysis",
    "Exploratory Data Analysis (EDA)",
    "Inferential Analysis",
    "Qualitative Analysis",
    "Quantitative Analysis",
    "Time Series Analysis",
    "Spatial Analysis"
    ]
    columns = df.columns.tolist()
    count=0
    if request.method == 'POST':
        selected_method = request.POST.get('selected_method')
        searched_data=df
        if selected_method == "Descriptive Analysis":
            val=request.POST.get("descriptiveMethod")
            searched_data=Descriptive(df)
            if val=="0":
                searched_data=searched_data.describe()
            elif val=="1":
                searched_data=searched_data.describe_obj()
            elif val=="2":
                searched_data=searched_data.unique_count()
            elif val=="3":
                searched_data= searched_data.correlation_matrix()
            elif val=="4":
                col1 = request.POST.get('column_nm')
                searched_data=searched_data.unique_values(col1)
            elif val=="5":
                searched_data=searched_data.info()
            else:
                request.session['searched_data'] = searched_data.to_dict(orient='records')
        #request.session['searched_data'] = searched_data.to_dict(orient='records')
        request.session['searched_data'] =searched_data.reset_index().to_dict(orient='records')
        searched_data=generate_table_html(searched_data)
        return render(request,'fileupload/analyze_data.html', {
            'columns': columns,
            'searched_data': searched_data,
            'methods':data_analysis_types,
        }) 
    else:
        return render(request,'fileupload/analyze_data.html', {
                'columns': columns,
                'searched_data': generate_table_html(df),
                'methods':data_analysis_types,
            })
        
     
def download_file(request,id):
    if id==1:
        searched_data=request.session.get("searched_data")
        searched_data=pd.DataFrame(searched_data)
        searched_data=searched_data.to_csv(index=False )
        if searched_data:
            response=HttpResponse(searched_data,content_type='text/csv')
            response['Content-Disposition']='attachment; filename="searched_data.csv"'
            return response
    else:
        modified_data = request.session.get('uploaded_data')
        modified_data =pd.DataFrame.from_dict(modified_data)
        modified_data=modified_data.to_csv(index=False) 
        if modified_data:
            response = HttpResponse(modified_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="modified_data.csv"'
            return response

    return HttpResponse("No data found.", status=404)



def visualize_data(request):
    plots = request.session.get('plot_html', None)
    plot_html = None
    plot_type = None
    uploaded_data_dict = request.session.get('uploaded_data') 
    if uploaded_data_dict:
        df = pd.DataFrame.from_dict(uploaded_data_dict)
        columns = df.columns.tolist()
        numerical_col=df.select_dtypes(include=['number']).columns
        categorical_col=df.select_dtypes(include=['object']).columns
    else:
        return render(request, 'fileupload/data_visualization.html', {'error': 'No data found in session'})

    if request.method == 'POST':
        plot_type = request.POST.get('plot_type')
        column_name1 = request.POST.get('column_name') 
        column_name2 = request.POST.get("column_name1")
        selected_columns = request.POST.getlist('selected_columns')
        if df.empty:
            return render(request, 'fileupload/data_visualization.html', {'error': 'DataFrame is empty'})

        if plot_type == 'bar':
            if column_name2 in numerical_col:
                grouped_data = df.groupby(column_name1)[column_name2].mean().reset_index()
                fig = px.bar(grouped_data,x=column_name1,y=column_name2,color_discrete_sequence=['blue'])
            else:
                fig=px.bar(df,x=column_name1,y=column_name2,color_discrete_sequence=['blue'])
        elif plot_type == 'line':
            fig = px.line(df, y=selected_columns, title=f'Line Plot')
        elif plot_type == 'hist':
            function_input = request.POST.get("func_type")
            fig = px.histogram(df, x=column_name1, title=f'Histogram of {column_name1}',histfunc=function_input,nbins=5)
        elif plot_type=='scatter':
            fig = px.scatter(df,x=column_name1,y=column_name2 , title=f'Scatter of {column_name1} x {column_name2}'.center(50),color_discrete_sequence=['tomato','light'])
        elif plot_type=="pie":
            fig=px.pie(df,names=column_name1,title=f"Pie Plot of {column_name1}")
        elif plot_type=="kde":
            fig=px.density_contour(df,x=column_name1,y=column_name2,title=f"kde")
        elif plot_type == 'box':
            fig=px.box(df,x=column_name1,title=f'boxplot of {column_name1}')
        else:
            return render(request, 'fileupload/data_visualization.html', {'error': 'Invalid plot type', 'columns': columns})

        # Convert the plot to HTML
        plot_html = fig.to_html()

        context = {
            'plot_html': plot_html,
            'plot_type': plot_type,
            'columns': columns,
        }
        return render(request, 'fileupload/data_visualization.html', context)
    else:
        context = {
            'plot_html': plot_html,
            'plot_type': plot_type,
            'columns': columns,
            'plots':plots,
        }
        return render(request, 'fileupload/data_visualization.html', context)

def generate_plots(request):
    plot_data = []
    uploaded_data_dict = request.session.get('uploaded_data')
    df = pd.DataFrame.from_dict(uploaded_data_dict)
    # Iterate through numerical columns
    for column in df.select_dtypes(include=['number']).columns:
        try:
            # Histogram
            fig = px.histogram(df, x=column)
            plot_data.append(fig.to_html(full_html=False))

            # Box Plot
            fig = px.box(df, x=column)
            plot_data.append(fig.to_html())

            # Scatter Plot
            for another_column in df.select_dtypes(include=['number']).columns:
                if another_column != column:
                    fig = px.scatter(df, x=column, y=another_column)
                    plot_data.append(fig.to_html())
                    break  # Only show one scatter plot per column

        except Exception as e:
            print(f"Error plotting for {column}: {e}")

    # Iterate through categorical columns
    for column in df.select_dtypes(include=['object']).columns:
        try:
            # Bar Plot
            fig = px.histogram(df, x=column)
            plot_data.append(fig.to_html())

            # Pie Chart
            fig = px.pie(df, names=column)
            plot_data.append(fig.to_html())

        except Exception as e:
            print(f"Error plotting for {column}: {e}")

    request.session['plot_html'] = plot_data
    return redirect('visualize_data')


def person_list(request):
    uploaded_data_dict = request.session.get('uploaded_data')
    df = pd.DataFrame.from_dict(uploaded_data_dict)
    columns=df.columns.to_list()
    query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'index')  # Default sorting by name
    entries_per_page = int(request.GET.get('entries', 10))  # Default entries per page

    # Search functionality
    #if query:
       # df = .contains(query, case=False)]  # Case-insensitive search

    # Sort functionality
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by)

    # Pagination
    paginator = Paginator(df.values.tolist(), entries_per_page)  # Convert DataFrame to list of lists
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Convert the current page DataFrame back to HTML
    columns = df.columns.tolist()
    people_html = pd.DataFrame(page_obj.object_list, columns=columns).to_html(classes='table table-striped', index=False)

    context = {
        'people_html': people_html,
        'query': query,
        'sort_by': sort_by,
        'entries_per_page': entries_per_page,
        'page_obj': page_obj,
        'columns': columns,
    }
    return render(request, 'fileupload/auto_plots.html', context)