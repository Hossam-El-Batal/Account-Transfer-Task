# Account-Transfer-Task


## Technologies Used

- **Frontend**: Django Template.
- **Backend**: Django
- **Database**:sqlite

  
## **Features**

- **import and update database with csv**: use this url : http://127.0.0.1:8000/api/import-accounts/
- **list accounts**: http://127.0.0.1:8000/api/list/
- **CRUD operations**: http://127.0.0.1:8000/api/transfer/
  
## Explaining technology, database and tools choices

- **sqlite3**: It is built into Django by default, making it easy to set up and integrate, it's inherently atomic for transactions, which ensures reliability in operations like account transfers or balance updates and finally bec the data set provided is small. 
- **pagination in listing accounts**: added pagination for better user experience and decreased latency
  
  




