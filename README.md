@https://t.me/phoenix_habit_bot
Трекер привычек:

Command Table:
First Header    | Second Header
-------------   | -------------
start           | Launch bot and start dialog
info            | Get information about bot possibilities 
setatarget      | Choose the goal you want to achieve
addpages        | Enter the number of pages read
progress        | See your stats for the month
donate          | Support bot team
----------------------------------------------------------------
Flow Chart
```mermaid
flowchart TD
    Start["/start command"] --> CommandI(Command input)
    CommandI --> CommandC{Command check}

    CommandC -->|"/setatarget"| SetTarget["/setatarget execution"]
    SetTarget --> SetTargetI["Name input"] --> SetTargetC{Name check}
    SetTargetC --> |"ERROR"| SetTargetI
    SetTargetC --> |"OK"| PagesI["Number of pages input"] --> PagesC{Number of pages check} 
    PagesC --> |"ERROR"|PagesI
    PagesC --> |"OK"| PagesGoalI["Pages Goal input"] --> PagesGoalC{Pages Goal check} 
    PagesGoalC --> |"ERROR"|PagesGoalI
    PagesGoalC --> |"OK"| PagesGoalE["Target Confirmation"]

    CommandC -->|"/addpages"| AddPages["/addpages execution"]
    AddPages --> AddPagesI["Pages input"] --> AddPagesC{Pages check}
    AddPagesC --> |"ERROR"| AddPagesI
    AddPagesC --> |"OK"| AddPagesE["Pages Confirmation"]

    CommandC -->|"/info"| H["/info execution"]
    CommandC -->|"/progress"| F["/progress execution"]
    CommandC -->|"{wrong command}"| G["Wrong command allert"]
```
