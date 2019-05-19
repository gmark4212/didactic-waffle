**About project**

This is a website where you can view the most current developer skills for employers. Such an indicator of the most sought-after technology in the industry at the time. For example, enter the title of the post - python developer. Displays a list of technologies required in the vacancies for this request in descending order of their frequency. That is, in the top will be the most popular technology, the study of which is worth spending time.


**How it works**

There is a Celery job queue on the server, in which, according to a certain schedule, workers are started to parse job data from popular job search portals. Data is stored in the MongoDB database.
Further, the client requests the data, there is a request to the API raised on Flask. The server gives JSON with data, the client-app (Vue.js) renders it on the page.

