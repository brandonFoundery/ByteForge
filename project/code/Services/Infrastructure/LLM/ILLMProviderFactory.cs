using System.Collections.Generic;

namespace ByteForgeFrontend.Services.Infrastructure.LLM;

public interface ILLMProviderFactory
{
    ILLMProvider GetProvider(string providerName);
    IEnumerable<string> GetAvailableProviders();
}