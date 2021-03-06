using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;

namespace Diagnostics.RuntimeHost.Services
{
    public class SearchServiceDisabled : ISearchService
    {
        private string QueryDetectorsUrl;
        private string QueryUtterancesUrl;
        private string RefreshModelUrl;
        private string FreeModelUrl;
        private string TriggerTrainingUrl;
        private string TriggerModelRefreshUrl;

        public SearchServiceDisabled()
        {
        }

        public Task<HttpResponseMessage> SearchDetectors(string requestId, string query, Dictionary<string, string> parameters)
        {
            return Task.FromResult<HttpResponseMessage>(null);
        }

        public Task<HttpResponseMessage> SearchUtterances(string requestId, string query, string[] detectorUtterances, Dictionary<string, string> parameters)
        {
            return Task.FromResult<HttpResponseMessage>(null);
        }

        public Task<HttpResponseMessage> TriggerTraining(string requestId, string trainingConfig, Dictionary<string, string> parameters)
        {
            return Task.FromResult<HttpResponseMessage>(null);
        }

        public Task<HttpResponseMessage> TriggerModelRefresh(string requestId, Dictionary<string, string> parameters)
        {
            return Task.FromResult<HttpResponseMessage>(null);
        }

        public void Dispose()
        {
        }
    }
}
