
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export async function humanizeLegacy(bio: string, dreams: string[]): Promise<string> {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `بناءً على المعلومات التالية: "نبذة: ${bio}. أحلام: ${dreams.join(', ')}"، اكتب نصاً إنسانياً قصيراً ومؤثراً (بحدود 50 كلمة) يبرز الجانب الإنساني لهذه الشخصية كإنسان كان يحب الحياة. استخدم لغة محايدة ومحترمة بعيداً عن الشعارات السياسية.`,
      config: {
        temperature: 0.7,
        topP: 0.95,
      }
    });
    return response.text || "لا يتوفر نص حالياً.";
  } catch (error) {
    console.error("Error humanizing story:", error);
    return "نص إنساني يوثق رحلة حياة مليئة بالأحلام.";
  }
}
