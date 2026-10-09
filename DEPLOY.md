# Deploy QQQ Holdings vs TLT Weekly on Streamlit

1. Create the small database:

   python export_streamlit_db.py

2. Test locally:

   streamlit run dashboard.py

3. Create a public GitHub repo, for example:

   qqq-holdings-vs-tlt-weekly

4. Push:

   git init
   git add .
   git commit -m "Initial QQQ vs TLT weekly dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/qqq-holdings-vs-tlt-weekly.git
   git push -u origin main

5. In Streamlit Community Cloud use:

   Repository: YOUR_USERNAME/qqq-holdings-vs-tlt-weekly
   Branch: main
   Main file path: dashboard.py

6. For future weekly updates:

   python export_streamlit_db.py
   git add data/streamlit_data.sqlite
   git commit -m "Update weekly data"
   git push
