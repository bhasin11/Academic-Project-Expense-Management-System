# Fault Tolerant Web Application

Abstract

Built a fault tolerant expense mamagement system using Python Flask.

Prerequisites

Base URL: http://localhost:5000
POST /v1/expenses
Request Body

{
    "name" : "Foo Bar",
    "email" : "foo@bar.com",
    "category" : "office supplies|travel|training",
    "description" : "iPad for office use",
    "link" : "http://www.apple.com/shop/buy-ipad/ipad-pro",
    "estimated_costs" : "700",
    "submit_date" : "09-08-2016"
}
Response Header

201 Created
Response Body

{
    "id" : "123456",
    "name" : "Foo Bar",
    "email" : "foo@bar.com",
    "category" : "office supplies|travel|training",
    "description" : "iPad for office use",
    "link" : "http://www.apple.com/shop/buy-ipad/ipad-pro",
    "estimated_costs" : "700",
    "submit_date" : "09-08-2016",
    "status" : "pending",
    "decision_date" : ""
}
GET /v1/expenses/{expense_id}
Response Header

200 OK
Response Body

{
    "id" : "123456",
    "name" : "Foo Bar",
    "email" : "foo@bar.com",
    "category" : "office supplies|travel|training",
    "description" : "iPad for office use",
    "link" : "http://www.apple.com/shop/buy-ipad/ipad-pro",
    "estimated_costs" : "700",
    "submit_date" : "09-08-2016",
    "status" : "pending",
    "decision_date" : ""
}
PUT /v1/expenses/{expense_id}
Request Body

{
    "estimated_costs" : "800"
}
Response Header

202 Accepted
DELETE /v1/expenses/{expense_id}

Response Header

204 No Content
Data Persistence

Database:
Stored data generated from the APIs into MySQL RDBMS using Flask-SQLAlchemy.

Docker Container Persistence

Docker provides Data containers for stateful applications like Database. Mounted a dedicated volume for MySQL so that you can easily manage the persistence data file generated from MySQL.

Achieved the following:

Dynamic Replica Registration
Dynamic Load Balancing
Failure Detection


Requirements

Dynamic Replica Registration
A component called Router is implemented based on this tiny Python TCP proxy server.

As part of the node registration, whenever a new expense management application's Docker instance is launched, it will auto-register to the own instance to the router.

Failure Detection (via CircutBreaker)
Whenever a node reaches its CircuitBreaker's error count, the router will deregister the failed node from the routing table in Redis and forward the same request to the next available node.
