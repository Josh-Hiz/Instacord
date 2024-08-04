

- ALL OF THIS SHOULD WORK, TEST THOROUGHLY: CREATE TWO POST CHECKERS FOR SAME ACCOUNT, AND THEN CALL last_post BEFORE IT AUTO PRINTS FOR ONE OF THEM
  - EDIT post_data_D file to make sure last_post and last_post_author work
    - post_checker needs to return last_post, and the value should be updated in the class
    - main FILE SHOULD BE FINE
    - works for one because globals are still there, prolly should not work (nvm doesnt work beyond first iteration)

  - REMOVE THE USE OF GLOBAL VARIABLES FOR last_post and last_post_author 

  - MAKE post_check_task COMPLETELY SELF CONTAINED (TO RUN IN MULTIPLE SERVERS SIMULTANEOUSLY)
    - REMOVING GLOBAL VARIABLES
    - REDOING START, PAUSE, CANCEL COMMANDS

- CREATE FUNCTION JUST FOR PRINTING A GIVEN POST
  - IN THE MAIN LASTPOST/POSTCHECK FUNCTION, GET A LIST OF ALL NEW POSTS
  - THEN LOOP THROUGH EACH POST, AND FOR EACH POST CALL THE PRINT FUNCTION

- ADJUST NONDOWNLOAD FUNCTIONS LIKE HOW DOWNLOAD FUNCTIONS ARE

- ADD FOR *STORIES* and *THREADS*
