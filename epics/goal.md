EPICS 3rd year CSE project
had to make something that was usefull to the community 
so we chose this project

the project is as follows:
we have planned to make a all in one medical app.
The intended flow of app is as follows:
for all you health related needs a patient will come to this app,
say they are sick, they will open a case put in thier symptoms 
enter thier vitals (say someone is in a small village where the doctor is a generic doc, but the patient might need a specific specialist) so the village doctor will take the symptoms and vitals for the dude.
like bp, heart rate, etc
and enter that in our system.
the system would also store geographical location and maybe some other meta data.
Now based on the symptoms and vitals OR maybe based on the doctors recommendation of specialists, say a gynecologist is needed as per the doctor, if the local doctor has a recommendation that would be used at higher priority but under a world (like say covid, or the person simply is'nt sure which doctor to visit first), then entry can be made by patient alone, in which case the specialist would be recommended by LLM model based on symptoms and vitals.
Now say we decided that we have to look for a gyno, so the algorithm would search for doctors based on geographical proximity and budget of patient (whether he/she has insurance or not, till what amount does the insurance cover and so on)

Now a specialist is choosen Say X, so the system itself would keep track of all 3, the list of specialists working on that patient case (including the inital general doctor)

and whatever medical reports have been taken like say blood test, etc would be accessible from the website to all doctors who wish to work on this case and to patient.

The complete medical history from all cases would also be tracked seperately.

The aggregate fo medical information would be used to predict any kind of diseases that user might face down the line and suggest visinting appropriate doctors based on it. From newly found allergies (say from some other case we found out that the paitent was allergic to Medicine X and the reaction was Y, so then if in some other case some other docotor recommends some medicine, our service/app/web would warn the doctor and bring up relevant documents so that the doctor can change the prescription.

So the flow would feel like this:
village patient visits local doctor, local doctor tries to treat them, all the treatment (vitals recorded, medicne prescribed, dosage, etc)) would be recorded in the database and used for analytics. Then if the patient still does not feel well and a specialist is added to the case (virtually the speicalist can be america and the patient can be in india) the specialist will see the reports and suggest some tests to be done or some new meicines to be perescribed etc all via our app/service.

Then say the patient is treated but faces the same issue after 5 years, if our app was not availble then most likely a village paitent might have lost all the relevant docs from 5 years ago, but our app would keep it stored.

(The benefit of storing medical history is not just limited to that specific human, it can be used by generations to come for to predict genetic diseases early and take prenvetive measure not just for that human but for generations to come for based on the entire statistical data of family tree (assuming everyone in the family uses such service))

A statistical model would give various kinds of medical insigts of predictive, preventive, etc or the current mistake (pattern) that might be cusing current issue, etc.


This is the core idea, implementation relies entirely on the implementer, the UI/UX should be friendly and fast enought to not waste too much time of doctors and for easy and quick access of cases (medical cases)

note: One way was to for the patient/ generic doctor to select from a list of specialist docotrs, 
but it could be technically the other way around (that is the specialist looks through different cases and picks up the case they feel they should take )

Also, maybe we could add scedule manager for doctors like you have a virtual meeting with so and so patient at so and so time, etc. Thus maybe our service should support virtual calling.
