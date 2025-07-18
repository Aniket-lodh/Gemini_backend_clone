# Gemini Chatroom Backend Clone

This project is a backend implementation of a Gemini Chatroom clone, built with FastAPI, PostgreSQL, Redis, Celery, and Stripe for subscription management.

## Features

- **User Authentication:** User registration and login.
- **Chatroom Management:** Create and list chatrooms.
- **Messaging:** Send and receive messages within chatrooms, with Gemini integration for AI responses, Asynchronous processing via message queues (Celery).
- **Background Task Processing:** Asynchronous message processing using Celery.
- **Caching:** Improved performance through caching frequently accessed data with Redis.
- **Stripe Integration:** Subscription management with Stripe Checkout and webhooks.
- **Rate Limiting:** API rate limiting based on user subscription tier.

## Technologies Used

- **Language**: Python (FastAPI)
- **Database**: PostgreSQL
- **Queue**: Celery
- **Authentication**: JWT with OTP verification
- **Payments**: Stripe (sandbox environment)
- **External API**: Google Gemini
- **Deployment**: Fly.io

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Aniket-lodh/Gemini_backend_clone.git
   cd Gemini_backend_clone
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add the following variables:

   ```
   DATABASE_URL=postgresql://<username>:<password>@localhost/<database>
   STRIPE_SECRET_KEY=<your-stripe-secret-key>
   GEMINI_API_KEY=<your-gemini-api-key>
   ```

4. **Start the Application**:
   ```bash
   python server.py <- This starts main server.
   ```
   In a separate terminal again run
   ```bash
   python celery_worker.py <- This starts celery worker.
   ```
5. **Check Api Docs**:
    Navigate to /scalar to view api documentation of this application, you can perform your requests there.

## API Endpoints

### Authentication

- **POST /auth/signup**: Register a new user with mobile number and optional info.
- **POST /auth/send-otp**: Sends an OTP to the user’s mobile number (mocked).
- **POST /auth/verify-otp**: Verifies the OTP and returns a JWT token.
- **POST /auth/forgot-password**: Sends OTP for password reset (OTP mocked).
- **POST /auth/change-password**: Allows the user to change password while logged in.

### User Management

- **GET /user/me**: Returns details about the currently authenticated user.

### Chatroom Management

- **POST /chatroom**: Creates a new chatroom for the authenticated user.
- **GET /chatroom**: Lists all chatrooms for the user (cached).
- **GET /chatroom/:id**: Retrieves detailed information about a specific chatroom.
- **POST /chatroom/:id/message**: Sends a message and receives a Gemini response.

### Subscription Management

- **POST /subscribe/pro**: Initiates a Pro subscription via Stripe Checkout.
- **GET /subscription/status**: Checks the user's current subscription tier.

### Webhook

- **POST /webhook/stripe**: Handles Stripe webhook events (checkout.session.completed / checkout.session.expired).

## How I Built It

I wanted this backend to be **fast**, **scalable**, and **affordable**. So made a few key decisions:

### FastAPI + SQLModel

FastAPI gave us automatic OpenAPI docs and async support out of the box. SQLModel (built on SQLAlchemy and Pydantic) kept database models and request validation super clean.

### Queue System Explanation

Celery is used to handle asynchronous calls to the Google Gemini API. When a user sends a message, it is placed in a queue, allowing the application to respond quickly while processing the message in the background.

### Redis Caching + Pub/Sub

I didn’t want the server to hit the DB or Gemini API unnecessarily or maybe reduce the load atleast. Redis caches user plans, tokens, and even recent responses to speed things up. It also acts as the message broker for Celery.

## Gemini API Integration Overview

The application integrates with the Google Gemini API to provide AI-powered responses to user messages. The integration is handled asynchronously via Celery.

### Stripe Integration

Subscriptions are managed through Stripe. We use webhooks to listen for events like checkout completion or subscription updates. These webhook endpoints update our local user plan data.

### Rate Limiting per Plan

Added a basic rate limiting mechanism. Free users get limited requests per minute/hour, while pro users (via Stripe) get more generous limits.

## Assumptions/Design Decisions

- The application assumes that users will primarily interact via mobile numbers for authentication.
- Caching is implemented for the chatroom listing to reduce database load and improve performance.
- Rate limiting is applied to Basic tier users to manage usage effectively.

## Testing via Postman

A Postman collection is provided to test all API endpoints. Import the collection into Postman and use the provided JWT tokens for authenticated routes.
If you dont want to use via postman, you can also navigate to '/scalar' endpoint to access the api routes.

## Steps to Deploy

- First, install Fly CLI if you haven’t already:
  ```bash
  https://fly.io/docs/hands-on/install-flyctl/
  ```
- Then login to fly via flyctl:
  ```bash
  fly auth login
  ```
- Then deploy:
  ```bash
  fly deploy
  ```
- Set env variables:
  ```bash
  fly secrets set STRIPE_SECRET_KEY=your_key GEMINI_API_KEY=your_key ...
  ```
