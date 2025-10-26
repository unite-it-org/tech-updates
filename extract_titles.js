const fs = require('fs');

const text = `Here are the titles about new technology from the provided list:

*   Microsoft is giving Copilot AI faces you can chat with
*   Google’s AI Mode image search is getting more conversational
*   Microsoft’s new Security Store is like an app store for cybersecurity
*   OpenAI’s new social video app will let you deepfake your friends
*   Windows 11’s 2025 update is available now
*   OpenAI’s Sora App Creates Realistic AI Videos of You and Your Friends
*   Adobe Launches Premiere for iPhone and iPad
*   Alexa+: Amazons neue Assistentin ist endlich final
*   Sora launches on App Store for iPhone video creation from ChatGPT maker
*   Opera releases Neon, its AI-powered browser with a built-in agent
*   Nvidia’s CEO Jensen Huang says electricians and plumbers will be needed by the hundreds of thousands in the new working world
*   Meta to buy chip startup Rivos for AI effort, source says`;

const delimiter = `Here are the titles about new technology from the provided list:

`;

const titlesPart = text.split(delimiter)[1];

const titles = titlesPart.split('\n').map(title => title.replace('*   ', '').trim()).filter(title => title.length > 0);

const sampleData = JSON.parse(fs.readFileSync('sample1.json', 'utf-8'));
const articles = sampleData[0].articles;

const matchingArticles = articles.filter(article => {
    return titles.some(title => article.title && article.title.includes(title));
});

console.log(matchingArticles);



