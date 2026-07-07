QR Classroom Portal

Local development & upload notes

- Start backend:
	- cd backend
	- npm run dev

- Start frontend:
	- cd frontend
	- npm run dev

- Default teacher account (created for local testing):
	- Email: teacher@example.com
	- Password: teacher123

- Uploading materials:
	- Allowed types: PDF, DOCX, PPTX
	- Open the frontend at `http://localhost:5175/`, login, go to `Upload Notes` and submit the form.
	- Uploaded files are served from the backend at `http://localhost:5000/uploads/<filename>`

