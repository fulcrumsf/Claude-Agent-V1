import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');
const envPath = path.join(rootDir, '.env');

// Simple .env parser
function getEnvKey() {
    if (!fs.existsSync(envPath)) {
        console.error("❌ .env file not found at " + envPath);
        return null;
    }
    const content = fs.readFileSync(envPath, 'utf-8');
    const match = content.match(/VITE_GEMINI_API_KEY=(.*)/);
    if (!match || !match[1]) {
        console.error("❌ VITE_GEMINI_API_KEY not found in .env");
        return null;
    }
    return match[1].trim();
}

async function run() {
    console.log("🔍 Diagnosing Gemini API Connection...");

    const API_KEY = getEnvKey();
    if (!API_KEY) return;

    console.log(`🔑 API Key found: ${API_KEY.substring(0, 5)}...${API_KEY.substring(API_KEY.length - 4)}`);
    console.log("----------------------------------------");

    const genAI = new GoogleGenerativeAI(API_KEY);

    try {
        console.log("📡 Attempting to list available models via raw REST API...");

        const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${API_KEY}`;
        const response = await fetch(url);

        if (!response.ok) {
            console.error(`❌ List Models Failed. Status: ${response.status} ${response.statusText}`);
            const errorText = await response.text();
            console.error("   Response:", errorText);
            return;
        }

        const data = await response.json();
        const models = data.models || [];

        console.log(`✅ Connection Successful! Found ${models.length} models.`);

        if (models.length === 0) {
            console.warn("⚠️  Key is valid, but NO models are available.");
            return;
        }

        console.log("----------------------------------------");
        console.log("Available Models:");
        models.forEach(m => {
            if (m.supportedGenerationMethods && m.supportedGenerationMethods.includes("generateContent")) {
                console.log(`- ${m.name}`);
            }
        });
        console.log("----------------------------------------");

        // Now test the first available model
        const firstModel = models.find(m => m.supportedGenerationMethods && m.supportedGenerationMethods.includes("generateContent"));

        if (firstModel) {
            const shortName = firstModel.name.replace("models/", "");
            console.log(`\n🧪 Testing generation with: ${shortName}`);

            const model = genAI.getGenerativeModel({ model: shortName });
            try {
                const result = await model.generateContent("Hello!");
                console.log(`✅ GENERATION SUCCESS!`);
                console.log(`   Response: "${result.response.text().substring(0, 50)}..."`);
            } catch (e) {
                console.error("❌ Generation Failed:", e.message);
            }
        }

    } catch (error) {
        console.error("❌ Unexpected Error:", error);
    }
}

run();
