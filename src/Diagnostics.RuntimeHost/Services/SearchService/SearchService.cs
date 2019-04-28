using Diagnostics.ModelsAndUtils.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using System.Web;
using Diagnostics.RuntimeHost.Utilities;

namespace Diagnostics.RuntimeHost.Services
{
    public interface ISearchService : IDisposable
    {
        Task<HttpResponseMessage> SearchDetectors(string requestId, string query, Dictionary<string, string> parameters);

        Task<HttpResponseMessage> SearchUtterances(string requestId, string query, string[] detectorUtterances, Dictionary<string, string> parameters);
    }

    public class SearchService : ISearchService
    {
        private string QueryDetectorsUrl;
        private string QueryUtterancesUrl;
        private string RefreshModelUrl;
        private string FreeModelUrl;
        private HttpClient _httpClient;
        
        public SearchService()
        {
            QueryDetectorsUrl = UriElements.SearchAPI + "/queryDetectors";
            QueryUtterancesUrl = UriElements.SearchAPI + "/queryUtterances";
            InitializeHttpClient();
        }

        public Task<HttpResponseMessage> Get(HttpRequestMessage request)
        {
            return _httpClient.SendAsync(request);
        }

        public Task<HttpResponseMessage> SearchDetectors(string requestId, string query, Dictionary<string, string> parameters)
        {
            parameters.Add("text", query);
            parameters.Add("requestId", requestId ?? string.Empty);
            HttpRequestMessage request = new HttpRequestMessage(HttpMethod.Post, QueryDetectorsUrl);
            request.Content = new StringContent(JsonConvert.SerializeObject(parameters), Encoding.UTF8, "application/json");
            return Get(request);
        }

        public Task<HttpResponseMessage> SearchUtterances(string requestId, string query, string[] detectorUtterances, Dictionary<string, string> parameters)
        {
            parameters.Add("detector_description", query);
            parameters.Add("detector_utterances", JsonConvert.SerializeObject(detectorUtterances));
            parameters.Add("requestId", requestId);
            HttpRequestMessage request = new HttpRequestMessage(HttpMethod.Post, QueryUtterancesUrl);
            request.Content = new StringContent(JsonConvert.SerializeObject(parameters), Encoding.UTF8, "application/json");
            return Get(request);
        }

        public void Dispose()
        {
            if (_httpClient != null)
            {
                _httpClient.Dispose();
            }
        }

        private void InitializeHttpClient()
        {
            _httpClient = new HttpClient
            {
                MaxResponseContentBufferSize = Int32.MaxValue,
                Timeout = TimeSpan.FromSeconds(30)
            };

            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        }

        private string AppendQueryStringParams(string url, string query, string productid)
        {
            var uriBuilder = new UriBuilder(url);
            var queryParams = HttpUtility.ParseQueryString(uriBuilder.Query);
            queryParams.Add("text", query);
            queryParams.Add("productid", productid);
            uriBuilder.Query = queryParams.ToString();
            return uriBuilder.ToString();
        }
    }
}