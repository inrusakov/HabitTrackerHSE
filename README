@https://t.me/phoenix_habit_bot
Трекер привычек:

###Command Table

First Header    | Second Header
-------------   | -------------
start           | Launch bot and start dialog
info            | Get information about bot possibilities 
setatarget      | Choose the goal you want to achieve
addpages        | Enter the number of pages read
progress        | See your stats for the month
donate          | Support bot team

###FlowChart

```flow
st=>start: /start
com=>operation: Command input
cond1=>condition: /setatarget
cond2=>condition: /addpages
cond3=>condition: /progress
e=>end: Command execution
err=>end: Command failure

st->com->cond1
cond1(yes)->e
cond1(no)->cond2
cond2(yes)->e
cond2(no)->cond3
cond3(yes)->e
cond3(no)->err
```