import re
import time
import streamlit as st
import streamlit as st
from fpdf import FPDF
#from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
#from azure.storage.blob import ContentSettings
from datetime import datetime, timedelta
import langchain
from langchain.chat_models import ChatOpenAI
from PIL import Image
import os

from langchain.prompts.chat import(
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

langchain.verbose = False
OPENAI_API_KEY= 0

connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
container_name = "aicoursegenerator"
#account_name = os.environ.get("AZURE_STORAGE_ACCOUNT", "")

page_title = os.environ.get("PAGE_TITLE", "Course Bee")

page_icon = Image.open("images/logo.png")

PAGE_CONFIG = {"page_title":page_title,
               "page_icon": page_icon, 
               "layout":"centered",  
               "initial_sidebar_state":"auto"}

st.set_page_config(**PAGE_CONFIG)


# generate the technical course
def generate_course(subject, Length_of_course, Activities_in_course, Difficulty_Level,Target_Audience,main_image,model_name):
    main_image.empty()
    with st.spinner('Generating course...'):
        chat = ChatOpenAI(

            openai_api_key=OPENAI_API_KEY,

            model_name=model_name,

            temperature=0,

            request_timeout=180,

            streaming=True)

 

 
        sys_message="As a highly accomplished '{subject}' course creator, you have extensive expertise in developing comprehensive, end-to-end '{subject}' courses"
        system_message_prompt=SystemMessagePromptTemplate.from_template(sys_message)

        Human_template= """
        What modules should be included in the course '{subject}' for the difficulty level '{Difficulty_Level}'?
        Return back a list that gives heading of each module. Do not include any context or pretext.

        """

        human_message_prompt=HumanMessagePromptTemplate.from_template(Human_template)

        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

        response=chat(chat_prompt.format_prompt(subject=subject,Difficulty_Level=Difficulty_Level).to_messages()).content

        Modules_list=response
        st.header("Modules")
        st.write(Modules_list)
        
        # count the number of modules
        count = len(Modules_list.split("\n"))
        # Number of modules to be generated. 
        mod_num=st.selectbox("Number of modules to generate", options=[i for i in range(1, count+1)], index=0)
        # Parse response back into a list
        Modules=re.sub(r"^\d+\.\s*","",response,flags=re.MULTILINE).split('\n')
        human_template="""
        Create an outline for a course module on {module} within the course context of these following modules as not to be redundant:
        {Modules_list}

        ----

        Return the response in a JSON formatted structure with following

        keys: Course Title, Module Outline and within it a Section Title and Section Content for each module. Keep the content detailed\
        and descriptive and add the coding excercises with it.
        """


        human_message_prompt=HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

        for module in Modules[:1]:
            response=chat(chat_prompt.format_prompt(module=module,subject=subject,Modules_list=Modules_list).to_messages()).content
            #print(response)
            outline=eval(response)


        human_template="""

        You are a {subject} course creator. Your task is to explain in detail about the '{content}'for the '{title}' section of the Course Title '{Course Title}' for a course on 
        {subject}. You have to explain in detail whatever is written in {content} and it should be complete text with code snippets of each topic in '{content}'.
        You have to write the code for each topic you mention in the {content}.Keep the code snippet background of different color.You have to add the following in output:
         
        
        1. Add the coding exercise with relevant topics which require coding exercises.
        2. There should be detailed description of each topic mentioned in "{content}"
        3. Create bold headings for the Topics and their sub headings mentioned in the "{content}" and keep these headings format consistent throughout.
        4. There must be quiz of multiple choice questions from each of the coding exercise you create and keep the
           answer options of those multiple choice questions in vertical line and not in the same line as the quiz question.
        5. Add Module overview and learning objectives in the start of each "{title}" and keep the each section very detailed.
        6. Add real life example and additional information for each topic mentioned in "{content}"
        7. Always add the conclusion at the end of each Module.
        8. Keep the each "{title}" heading prominent and bold
        9. Make sure to keep the output format consistent all the time.
        10.Remove the formatting symbols around headings from the generated output text.
        11.Do not repeat the Module content and headings
        12.Clearly show headings of each topic in the module and always mentionsthe Heading of module before It is started.
        


        """


        human_message_prompt=HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])
            
        text=""

        for section in outline['Module Outline'][:mod_num]:
            title = section["Section Title"]
            content = section["Section Content"]
            print(title, content)
            response = chat(
                chat_prompt.format_prompt(
                    content=content,
                    title=title,
                    subject=subject,
                    Length_of_course=Length_of_course,
                    Activities_in_course=Activities_in_course,
                    Difficulty_Level=Difficulty_Level,
                    Target_Audience=Target_Audience,
                    **outline
                ).to_messages()
            ).content
            text += response + "\n\n"
            text=text.replace("**", "").replace("*", "")
            st.write(response)
            time.sleep(5)


         # Create a PDF file from the generated text
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 15)
        pdf.multi_cell(0, 10, txt = text)
        pdf_filename = f"{subject}_course"
        pdf.output(pdf_filename)

        with open(pdf_filename, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        
        blob_html = generate_blob_link(subject, PDFbyte)
        st.write(blob_html, unsafe_allow_html=True)
        
# generate the theoretical course
def generate_theoretical_course(subject, Length_of_course, Activities_in_course, Difficulty_Level,Target_Audience,main_image,model_name):
    main_image.empty()
    with st.spinner('Generating course...'):
        chat = ChatOpenAI(

            openai_api_key=OPENAI_API_KEY,

            model_name=model_name,

            temperature=0,

            request_timeout=180,

            streaming=True)

 
        sys_message="As a highly accomplished '{subject}' course creator, you have extensive expertise in developing comprehensive, end-to-end '{subject}' courses"
        system_message_prompt=SystemMessagePromptTemplate.from_template(sys_message)

        Human_template= """
        What modules should be included in the course '{subject}' for the difficulty level '{Difficulty_Level}'?
        Return back a list that gives heading of each module. Do not include any context or pretext.

        """

        human_message_prompt=HumanMessagePromptTemplate.from_template(Human_template)

        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

        response=chat(chat_prompt.format_prompt(subject=subject,Difficulty_Level=Difficulty_Level).to_messages()).content

        Modules_list=response
        
        st.header("Modules in a Course")
        st.write(Modules_list)
        # count the number of modules
        count = len(Modules_list.split("\n"))
        # Number of modules to be generated. 
        mod_num=st.selectbox("Number of modules to generate", options=[i for i in range(1, count+1)], index=0)
        # Parse response back into a list
        Modules=re.sub(r"^\d+\.\s*","",response,flags=re.MULTILINE).split('\n')
        human_template="""
        Create an outline for a course module on {module} within the course context of these following modules as not to be redundant:
        {Modules_list}

        ----

        Return the response in a JSON formatted structure with following

        keys: Course Title, Module Outline and within it a Section Title and Section Content for each module. Keep the content detailed
        and descriptive.
        """


        human_message_prompt=HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

        for module in Modules[:1]:
            response=chat(chat_prompt.format_prompt(module=module,subject=subject,Modules_list=Modules_list).to_messages()).content
            #print(response)
            outline=eval(response)


        human_template="""

        You are a {subject} course creator. Your task is to explain in detail about the '{content}'for the '{title}' section of the Course Title '{Course Title}' 
        for a course on {subject}. You have to explain in detail whatever is written in {content} and it should be complete text with detailed description of each topic 
        in '{content}'.You have to add the following in output:
         
        
       
        1. There should be detailed description of each topic mentioned in "{content}" and also use the given language to print the completions
            for example if it says "{content}" in Arabic then use arabic language as output.
        2. Create bold headings and use different fonts for the Topics headings and their sub headings mentioned in the "{content}" 
            and keep these headings format consistent throughout.
        4. There must be quiz of multiple choice questions from each of the topics mentioned in "{content}" and keep the
           answer options of those multiple choice questions in vertical line and not in the same line as the quiz question.also
           provide the answers in the end.
        5. Add Module overview and learning objectives in the start of each "{title}" and keep the each section very detailed.
        6. Add real life example and additional information for each topic mentioned in "{content}"
        7. Always add the conclusion at the end of each Module.
        8. Keep the each "{title}" heading prominent and bold
        8. Make sure to keep the output format consistent all the time.
        9. The output format should be PDF oriented so that headings appear bold in pdf file.
        10. Remove the formatting symbols around headings from the generated output text.
        11. Do not repeat the Module content and headings
        12. 12.Clearly show headings of each topic in the module and always mentionsthe Heading of module before It is started.

        """


        human_message_prompt=HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])
            
        # Course_title = outline['Course Title']
        text=""

        for section in outline['Module Outline'][:mod_num]:
            title = section["Section Title"]
            content = section["Section Content"]
            print(title, content)
            response = chat(
                chat_prompt.format_prompt(
                    content=content,
                    title=title,
                    subject=subject,
                    Length_of_course=Length_of_course,
                    Activities_in_course=Activities_in_course,
                    Difficulty_Level=Difficulty_Level,
                    Target_Audience=Target_Audience,
                    **outline
                ).to_messages()
            ).content
            text += response + "\n\n"
            text=text.replace("**", "").replace("*", "")
            st.write(response)
            time.sleep(5)
             # Create a PDF file from the generated text
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 15)
        pdf.multi_cell(0, 10, txt = text)
        pdf_filename = f"{subject}_course"
        pdf.output(pdf_filename)
        
        

        with open(pdf_filename, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
    
    
def main():
    
    # Add picture on the side bar
    hide_footer_style = """
    <style>
    footer {visibility: hidden;}   
    </style> 
    """
    st.markdown(hide_footer_style, unsafe_allow_html=True)
    st.sidebar.title("Course Bee")
    image = Image.open('images/mainImage.png')
    main_image = st.image(image, use_column_width=True)
    st.sidebar.info("Generate course using AI co-pilot")
    mode = st.sidebar.selectbox("Choose Course Type", ["Technical Courses", "Theoretical Courses"])
    model_type = st.sidebar.selectbox("Choose Model Type", ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"])
    if mode == "Technical Courses":
        generate_courses_mode(main_image, model_type)
    else:
        generate_theoretical_courses_mode(main_image, model_type)
    
    hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
    st.markdown(hide_footer_style, unsafe_allow_html=True)

def generate_courses_mode(main_image, model_type):
    st.sidebar.subheader("Technical Course Details")
    
    placeholder_text = "Add a descriptive heading of the course"
    subject = st.sidebar.text_input("Name of the Course", value="", max_chars=None, key=None, type='default', help=None, on_change=None, args=None, kwargs=None, placeholder=placeholder_text)

    # CSS styling for the placeholder
    st.markdown(
        """
        <style>
        ::placeholder {
            color: lightgray;
            opacity: 0.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    
    Length_of_course = st.sidebar.selectbox("Length of the Course", ("30 minutes", "60 minutes", "90 minutes"))
    Activities_in_course = st.sidebar.selectbox("Activities in the Course", ("Quizzes", "Exercises"))
    Difficulty_Level = st.sidebar.selectbox("Difficulty Level", ("Beginner", "Intermediate", "Advanced"))
    Target_Audience = st.sidebar.selectbox("Target Audience", ("College Students", "Industry Professionals"))
    
    if st.sidebar.button("Generate Technical Course"):
        generate_course(subject, Length_of_course, Activities_in_course, Difficulty_Level, Target_Audience,main_image,model_type)

def generate_theoretical_courses_mode(main_image, model_type):
    st.sidebar.subheader("Theoretical Course Details")
    
    placeholder_text = "Add a descriptive heading of the course"
    subject = st.sidebar.text_input("Name of the Course", value="", max_chars=None, key=None, type='default', help=None, on_change=None, args=None, kwargs=None, placeholder=placeholder_text)

    # CSS styling for the placeholder
    st.markdown(
        """
        <style>
        ::placeholder {
            color: lightgray;
            opacity: 0.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    Length_of_course = st.sidebar.selectbox("Length of the Course", ("30 minutes", "60 minutes", "90 minutes"))
    Activities_in_course = st.sidebar.selectbox("Activities in the Course", ("Quizzes", "Exercises"))
    Difficulty_Level = st.sidebar.selectbox("Difficulty Level", ("Beginner", "Intermediate", "Advanced"))
    Target_Audience = st.sidebar.selectbox("Target Audience", ("College Students", "Industry Professionals"))
    if st.sidebar.button("Generate Theoretical Course"):
        generate_theoretical_course(subject, Length_of_course, Activities_in_course, Difficulty_Level, Target_Audience,main_image,model_type)
        
main()