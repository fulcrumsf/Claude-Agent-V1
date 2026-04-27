import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

const MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
];

const SYSTEM_INSTRUCTION = `You are Upkeeply, a smart home maintenance assistant.
Your goal is to help users track home assets (HVAC, appliances, etc.) and maintenance tasks.

You will receive a conversation history and potentially an image.
Analyze the latest request in the context of the history.

**CRITICAL: USE GOOGLE SEARCH**
If the user provides a model number or asks for technical specs (like "filter size", "manual", "maintenance schedule"), you MUST use the Google Search tool to find the *real* internet data. Do not hallucinate.
- Find the exact filter dimensions (e.g. 20x25x4).
- Find the manufacturer's maintenance intervals.
- Include these specific details in the 'notes', 'description', or 'asset' fields.

You must ALWAYS return a JSON object with this structure:
{
    "response": "Your conversational reply here.",
    "action": { ... } // Optional. Only include if you have enough info to create an asset or task.
}

Action Object Structure (if applicable):
{
    "asset": {
        "name": "Short name",
        "type": "hvac|appliance|plumbing|other",
        "location": "Room/Area",
        "manufacturer": "Brand",
        "model": "Model Number",
        "notes": "Any other details"
    },
    "task": {
        "title": "Short task title",
        "description": "What needs to be done",
        "frequencyType": "one_time|fixed_interval",
        "intervalDays": 90, // if fixed_interval
        "dueDate": "YYYY-MM-DD" // Default/Best guess
    },
    // INTERACTIVE SCHEDULING
    // If the task implies a recurring schedule (like "replace filter"), provide options for the user to pick.
    "frequencyOptions": [
        { "label": "3 Months", "days": 90 },
        { "label": "6 Months", "days": 180 },
        { "label": "1 Year", "days": 365 }
    ],
    "amazonSuggestions": [ 
            // CRITICAL: If the asset requires a physical part (filter, bulb, battery), you MUST suggest 1-2 generic Amazon items here.
            { "title": "Product Name", "price": "$10.00" }
    ]
}

**AMAZON RULE:** coverage is MANDATORY for consumables (filters, batteries, chemicals). If the user mentions a "filter", you MUST populate "amazonSuggestions".

If the user is correcting you (e.g., "The HVAC is in the basement"), acknowledge it in "response" and return the UPDATED "action" object reflecting the change so the UI can update the proposal.
If the user just wants to chat, return "action": null.
Do not use markdown code blocks for the JSON. Just return the raw JSON object.`;

// Initialize outside function to avoid creating multiple instances if possible,
// but we need to create model instances per request or at least per model type.
const genAI = new GoogleGenerativeAI(API_KEY || "mock-key");

export async function generateActionFromInput(history, existingAssets = []) {
    if (!API_KEY) {
        return { response: "I need a Gemini API Key to function correctly. Please add VITE_GEMINI_API_KEY to your environment." };
    }

    let lastError = null;
    let successfulModel = null;

    for (const modelName of MODELS_TO_TRY) {
        try {
            console.log(`[Upkeeply] Attempting to connect with model: ${modelName}`);

            // Check if model supports system instructions (Gemini 1.5+)
            const isV15 = modelName.includes("1.5");

            const modelConfig = {
                model: modelName,
                generationConfig: { responseMimeType: "application/json" }
            };

            // Only add system instruction via config for 1.5 models
            if (isV15) {
                const assetContext = existingAssets.length > 0
                    ? `\n\nEXISTING ASSETS (Do NOT create duplicates. If user refers to one of these, use its details):\n${JSON.stringify(existingAssets.map(a => ({ id: a.id, name: a.name, location: a.location })), null, 2)}`
                    : "";
                modelConfig.systemInstruction = SYSTEM_INSTRUCTION + assetContext;
            }

            const model = genAI.getGenerativeModel(modelConfig);

            // Convert internal message format to Gemini format
            let chatHistory = history
                .filter(msg => msg.role !== 'system')
                .map(msg => {
                    const parts = [{ text: msg.text }];
                    if (msg.image) {
                        try {
                            const base64Data = msg.image.split(',')[1];
                            if (base64Data) {
                                parts.push({
                                    inlineData: {
                                        data: base64Data,
                                        mimeType: "image/jpeg"
                                    }
                                });
                            }
                        } catch (e) {
                            console.warn("Failed to process image data", e);
                        }
                    }
                    return {
                        role: msg.role === 'user' ? 'user' : 'model',
                        parts: parts
                    };
                });

            // For older models (non-1.5), prepend system instruction to the first message if possible
            // or just rely on the prompt context.
            if (!isV15 && chatHistory.length > 0) {
                // Prepend system instruction to the first user message
                const firstMsgText = chatHistory[0].parts[0].text;
                const assetContext = existingAssets.length > 0
                    ? `\n\nEXISTING ASSETS (Do NOT create duplicates. If user refers to one of these, use its details):\n${JSON.stringify(existingAssets.map(a => ({ id: a.id, name: a.name, location: a.location })), null, 2)}`
                    : "";
                chatHistory[0].parts[0].text = `SYSTEM INSTRUCTION: ${SYSTEM_INSTRUCTION}${assetContext}\n\nUSER MESSAGE: ${firstMsgText}`;
            }

            // "history" for startChat is everything EXCEPT the last message
            const historyForChat = chatHistory.slice(0, -1);
            // The last message is what we "send"
            const lastMsg = chatHistory[chatHistory.length - 1];

            if (!lastMsg) {
                return { response: "I didn't receive any input." };
            }

            const chat = model.startChat({
                history: historyForChat,
            });

            const result = await chat.sendMessage(lastMsg.parts);
            const responseText = result.response.text();

            console.log(`[Upkeeply] Success with ${modelName}!`);
            successfulModel = modelName;

            try {
                return JSON.parse(responseText);
            } catch (e) {
                console.warn("JSON Parse failed, attempting cleanup", e);
                const cleanText = responseText.replace(/```json\n?|\n?```/g, "").trim();
                return JSON.parse(cleanText);
            }

        } catch (error) {
            console.warn(`[Upkeeply] Failed with model ${modelName}:`, error.message);
            lastError = error;
            // Continue to next model in loop
        }
    }

    // If we exit the loop, all models failed
    const errorDetails = lastError ? `${lastError.message}` : "Unknown error";
    return {
        response: `Sorry, I tried multiple AI models but couldn't connect to any of them. Please check your API key scope. Last error: ${errorDetails}`
    };
}
