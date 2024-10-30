
---

# Custom Polish Keyboard Layout Project

## 1. Data Preparation
### 1.1 Polish Language Corpus

- Collect diverse and representative text data in Polish to build a reliable corpus.

#### → Corpus from Speech - YouTube Transcriptions

##### → Idea

When typing on a keyboard, we likely use text that mirrors spoken language more than book or dictionary data. Therefore, it's a good idea to use transcriptions from YouTube videos to build the corpus. However, not many Polish videos have any transcriptions. While English videos generate transcriptions automatically for all content, we need to verify which Polish videos provide transcriptions and confirm that the videos are in Polish.
##### → Workflow
![Transcriptions Flowchart](Assets/images/DataRetrieveCorpus.png)

To ensure that we are working with Polish videos, a dictionary file was created containing Polish-specific words. These words were collected from several smaller dictionaries, with the condition that each word must contain at least one Polish national character (e.g., ó, ł, ć, ś, etc.). Some dictionaries had encoding issues, resulting in incorrect characters. A Python library was used to clean the file, and incorrect words were corrected to the first suggestion provided by the library. Duplicates were then removed, leaving 25,381 words (stored in the file `slownik.txt`).

Each word was then searched on YouTube, and the resulting videos (approximately 500 per word) were collected. This process took a few days, and duplicates were removed, resulting in 7,570,907 unique video URLs. The first Python script check, aimed at determining whether these videos had transcriptions, ran for over two months. To speed up the process, the script was split to run 10 requests in parallel.

### 1.2 Obtain Data from Speakleech

- Gather additional Polish language data using  Discord forums (like Speakleech) to enhance the corpus.

---

## 2. Idea Development
### 2.1 Key Considerations for Keyboard Design
- Identify key factors important in keyboard layouts (e.g., finger movement efficiency, alternation between hands, frequent letter placement).

### 2.2 Model Testing
- Define how to evaluate and test the effectiveness of the new keyboard layout.
- Establish metrics for speed, accuracy, and comfort.

### 2.3 Global Use for EN/PL Users
- Consider the layout's usability for both Polish and English typists.
- Investigate potential ways to optimize for bilingual users.

---

## 3. Model Creation
### 3.1 Deep Learning or Genetic Algorithm
- Choose between deep learning or a genetic algorithm for optimizing the keyboard layout.
- Outline pros and cons of each approach for this specific use case.

---

## 4. Testing and Results
### 4.1 Custom Test Creation
- Develop specific tests tailored to evaluate the new layout based on the Polish corpus.

### 4.2 Global Testing
- Use established tests to compare the new layout's efficiency with other layouts.
  
### 4.3 Comparative Analysis
- Benchmark the new layout against popular English layouts (e.g., QWERTY).
- Assess the layout’s performance with the Polish corpus and compare its efficiency.

---

## 5. Announcement and Community Engagement
### 5.1 Keylapp
- Launch the new layout through the Keylapp app or similar tools.

### 5.2 Discord and Online Forums
- Engage with communities like Discord and relevant online forums (e.g., keyboard design groups).

### 5.3 Reddit
- Share the project and results on Reddit for broader feedback and discussion.

---
