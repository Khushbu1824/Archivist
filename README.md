# Archivist

## Table of Contents

*   [Introduction](#introduction)
*   [Features](#features)
*   [Tech Stack](#tech-stack)
*   [Installation](#installation)
*   [Usage](#usage)
*   [Database Schema](#database-schema)
*   [Screenshots](#screenshots)
*   [Future Enhancements](#future-enhancements)

## Introduction 🎢

This is a comprehensive library management system built using Flask, Peewee ORM, and other Python libraries. It provides a user-friendly interface for managing books, members, transactions, and administrative tasks.  The system emphasizes security with password hashing, and offers features like membership management, book borrowing/returning, report generation, and more.

## Features ⭐

*   **User Authentication:** Secure login for members and administrators using bcrypt for password hashing.
*   **Book Management:** Add, edit, delete, and view books with details like title, author, ISBN, genre, etc.  Filtering by genre and search by author/title are also implemented.
*   **Membership Management:** Create, edit, delete, and view member profiles, including membership renewal functionality.
*   **Transaction Management:** Issue and return books, track borrowing history, and generate printable receipts.
*   **Admin Dashboard:** Overview of key statistics like total books, members, and borrowed books.
*   **Reporting:** Generate PDF reports of issued books for members.
*   **Search and Filter:** Search for books by title or author, and filter by genre.
*   **Image Integration:**  Images are displayed on various pages for visual appeal.

## Tech Stack 🛠️

*   **Frontend:** HTML, CSS, JavaScript (potentially with a framework like Bootstrap for styling)
*   **Backend:** Python (Flask framework)
*   **Database:** PostgreSQL (using Peewee ORM)
*   **PDF Generation:** WeasyPrint
*   **Security:** bcrypt for password hashing

## Installation 🔧

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/[username]/Library_management_application.git
    cd Library_management_application/
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt  # Create requirements.txt listing all dependencies
    ```

4.  **Database Configuration:**
    *   Create a PostgreSQL database.
    *   Set the database credentials in a `.env` file (see `models.py` for the expected format).

5.  **Run the Application:**
    ```bash
    flask run 
    ```

## Usage 🚀

1.  **Home Page:** Navigate to `http://localhost:5000` in your web browser.  You should see the home page with the welcome message and featured books (with images).

2.  **Apply for Membership:** Click on the "Apply for Membership" link and fill out the form (with an image of the form).

3.  **Books Section:** Browse books, filter by genre, and search by title or author (with an image demonstrating filtering and search).

4.  **Login:** Members can log in to view their borrowing history and perform actions like renewing their membership. Administrators can access the admin panel.

5.  **Admin Panel:** Access the admin panel to manage books, members, and transactions.

6.  **Borrowing/Returning Books:** Use the transaction forms (with image) to issue and return books.

7.  **Print Receipt:** After issuing books, download a PDF receipt with member details and a list of issued books.

8.  **Membership Renewal:** Use the membership renewal form (with image) to update membership expiry dates.

## Database Schema 🗄️

The database consists of the following tables:

*   **Admin:** Stores administrator user credentials.
*   **Book:** Stores book details (title, author, ISBN, genre, image URL, etc.).  `num_books_available` tracks the number of copies currently available.
*   **Membership:** Stores member information (name, DOB, contact details, membership type, expiry date, etc.).
*   **Transaction:** Tracks book borrowing/returning activities (member ID, book ID, issue date, return date, status).  Uses foreign keys to link to the `Membership` and `Book` tables.

(See `models.py` for a detailed schema definition using Peewee ORM.)

## Screenshots 📷

*(Include screenshots of the key pages here.)*

### Home Page

![Home Page 1](images/home1.png)  
![Home Page 2](images/home2.png)

*   Description: "The home page welcomes users with a captivating image of a classic library interior, creating an inviting atmosphere. It features a prominent welcome message and navigation links to key sections of the library system." 

### Membership Form

![Membership Form](images/membership.png)

*   Description: "The membership application form allows users to easily register for a library membership. It collects necessary personal details, contact information, and membership preferences."

### Book Section (Browsing and Filtering)

![Book Browsing](images/books3.png)
![Book Filtering](images/books2.png)
![Book Search](images/books1.png)

*   Description: "The book section provides an intuitive interface to browse the library's vast collection. Users can filter books by genre, as shown in the second image.  The third image shows how users can search for books by title or author." 

### Transaction Form (Issuing Books)

![Transaction Form](images/transaction.png)

*   Description: "The transaction form simplifies the process of issuing books to members. Librarians can select the member, choose the books to be issued, and specify the return date."

### Issued Books Page (Thank You/Confirmation)

![Issued Books Confirmation](images/thank_you.png)

*   Description: "After a successful transaction, the thank you page confirms the book issuance and provides a summary of the transaction details."

### Invoice/Receipt

![Invoice](images/invoice.png)

*   Description: "Users can download a PDF receipt containing the transaction details, including a list of issued books and member information."

### Login Page

![Login](images/login.png)

*   Description: "Members can securely access the system through the login page using their credentials."

### Membership Renewal Form

![Membership Renewal](images/membership_renewal.png)

*   Description: "Members can easily renew their memberships through this form by updating their expiry date."

### Return Book Form (Part 1)

![Return Book Form Part 1](images/return1.png)
![Return Book Form Part 2](images/return2.png)

*   Description: "The return book form allows members to initiate the return process.  It lists the books currently issued to the member."

### Admin Section

#### Admin Login

![Admin Login](images/admin_panel_login.png)

*   Description: "Administrators access the admin panel through a separate login page."

#### Admin Dashboard

![Admin Dashboard](images/admin_dashboard.png)

*   Description: "The admin dashboard provides an overview of key library statistics, including the total number of books, members, and currently borrowed books. It also offers quick links to manage books and members."

#### Member Management (List)

![Member List Part 1](images/memberslist1.png)
![Member List Part 2](images/memberslist2.png)

*   Description: "The member management section displays a list of all library members, allowing administrators to view, edit, and delete member profiles. Due to the list's length, it spans multiple screenshots."

#### Book Management (List)

![Book List Part 1](images/bookslist1.png)
![Book List Part 2](images/bookslist2.png)

*   Description: "The book management section provides a comprehensive list of all books in the library. Administrators can manage book details, add new books, and remove existing ones.  The list is shown across two images."

#### Add Book

![Add Book](images/add_book.png)

*   Description: "Administrators can add new books to the library's catalog using this form, providing details such as title, author, ISBN, genre, and cover image."

#### Edit Book Details

![Edit Book Details](images/edit_book_details.png)

*   Description: "Administrators can edit the details of existing books using this form, updating information such as title, author, publication date, and other relevant attributes."

## Future Enhancements 🚀

*   **User Interface Improvements:**  Enhance the UI with a modern CSS framework (like Bootstrap) and JavaScript for interactive elements.
*   **Advanced Search/Filtering:** Implement more sophisticated search options (e.g., by keyword, publication date).
*   **Automated Reminders:**  Send email reminders to members for overdue books.
*   **Online Payment Integration:**  Allow members to pay membership fees online.
*   **Reporting Enhancements:**  Generate more detailed reports (e.g., popular books, member activity).
*   **Unit Tests:** Add unit tests to ensure code quality and prevent regressions.
