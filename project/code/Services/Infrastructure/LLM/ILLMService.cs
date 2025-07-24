using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.LLM;

public interface ILLMService
{
    Task<LLMGenerationResponse> GenerateAsync(LLMGenerationRequest request, CancellationToken cancellationToken = default);
    Task<IEnumerable<LLMGenerationResponse>> GenerateBatchAsync(IEnumerable<LLMGenerationRequest> requests, CancellationToken cancellationToken = default);
    IEnumerable<string> GetAvailableProviders();
}