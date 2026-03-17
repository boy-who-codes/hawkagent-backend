from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from django.conf import settings

class HawkAgent:
    def __init__(self, provider_config):
        """
        provider_config: dict with 'type' (groq/openai/gemini), 'api_key', 'model'
        """
        self.provider_type = provider_config.get('type', 'groq')
        self.api_key = provider_config.get('api_key')
        self.model_name = provider_config.get('model', 'llama3-8b-8192')
        self.base_url = provider_config.get('base_url', None)

        if self.provider_type == 'groq':
            self.llm = ChatGroq(groq_api_key=self.api_key, model_name=self.model_name)
        elif self.provider_type == 'openai':
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name)
        elif self.provider_type == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(anthropic_api_key=self.api_key, model_name=self.model_name)
        elif self.provider_type == 'gemini':
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(google_api_key=self.api_key, model=self.model_name)
        elif self.provider_type == 'deepseek':
            # DeepSeek provides OpenAI compatible endpoints
            base = self.base_url or "https://api.deepseek.com"
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, openai_api_base=base)
        elif self.provider_type == 'grok':
            # xAI (Grok) provides OpenAI compatible endpoints
            base = self.base_url or "https://api.x.ai/v1"
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, openai_api_base=base)
        elif self.provider_type == 'sarvam':
            # Sarvam AI compatible endpoints
            base = self.base_url or "https://api.sarvam.ai/v1"
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, openai_api_base=base)
        elif self.provider_type == 'openrouter':
            base = self.base_url or "https://openrouter.ai/api/v1"
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, openai_api_base=base)
        else: # custom
            base = self.base_url if self.base_url else "http://localhost:11434/v1" # fallback to local ollama style
            self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, openai_api_base=base)
            
        self.parser = JsonOutputParser()

    def generate_outreach(self, lead_data, agency_info, mode="branded", framework="Hormozi"):
        """
        mode: 'branded' or 'anonymous'
        """
        identity_instr = ""
        if mode == "anonymous":
            identity_instr = "IMPORTANT: In this initial outreach, DO NOT mention the brand name '{agency_name}'. Focus only on the value and the specific gaps found. Refer to yourself as a growth specialist."
        else:
            identity_instr = "Standard Branded Mode: Introduce yourself from '{agency_name}' and highlight your specific expertise."

        prompt = ChatPromptTemplate.from_template("""
        You are HAWK AGENT, a high-converting growth operator.
        
        LEAD DATA:
        {lead_data}
        
        AGENCY INFO:
        {agency_info}
        
        IDENTITY MODE: {mode}
        {identity_instr}
        
        FRAMEWORK: {framework} ($100M Offers/Leads)
        - Focus on the "Grand Slam Offer."
        - Use specific hooks from the audit data if available.
        - Ensure NO hallucinations. Only use facts from lead data.
        
        Output as JSON:
        - subject: Catchy subject.
        - body: The outreach content.
        - hook: The specific personalized angle used.
        """)
        
        chain = prompt | self.llm | self.parser
        return chain.invoke({
            "lead_data": lead_data,
            "agency_info": agency_info,
            "mode": mode,
            "identity_instr": identity_instr,
            "framework": framework,
            "agency_name": agency_info.get('name', 'Our Agency')
        })

    def analyze_audit_findings(self, audit_results, role="Web Dev"):
        prompt = ChatPromptTemplate.from_template("""
        As a expert in {role}, analyze these website audit results and identify the TOP 3 "High-Value Gaps" 
        that would provide immediate ROI if fixed.
        
        AUDIT RESULTS:
        {audit_results}
        
        Output as a JSON list of objects: [{"title": "...", "description": "...", "impact": "..."}]
        """)
        
        chain = prompt | self.llm | self.parser
        return chain.invoke({
            "audit_results": audit_results,
            "role": role
        })

    def get_agent_executor(self, tools, system_prompt="You are a helpful AI assistant."):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        return AgentExecutor(agent=agent, tools=tools, verbose=True)
