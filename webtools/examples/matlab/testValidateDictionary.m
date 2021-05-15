%% Shows how to call hed-services to obtain a list of services
host = 'http://127.0.0.1:5000';
csrf_url = [host '/hed-services']; 
services_url = [host '/hed-services-submit'];
dictionary_file = '../data/good_dictionary.json';
json_text = fileread(dictionary_file);

%% Send an empty request to get the CSRF TOKEN and the session cookie
[cookie, csrftoken] = getSessionInfo(csrf_url);

%% Set the header and weboptions
header = ["Content-Type" "application/json"; ...
          "Accept" "application/json"; ...
          "X-CSRFToken" csrftoken; ...
          "Cookie" cookie];

options = weboptions('MediaType', 'application/json', 'Timeout', Inf, ...
                     'HeaderFields', header);
data = struct();
data.service = 'validate_json';
data.hed_version = '7.1.2';
%data.hed_version = '8.0.0-alpha.1';
data.check_for_warnings = true;
data.json_string = string(json_text);
data.json_display_name = 'json str';

%% Send the request and get the response for version 7.1.2
response = webwrite(services_url, data, options);
response = jsondecode(response);
fprintf('Error report: [%s] %s\n', response.error_type, response.error_msg);

%% Print out the results if available
if isfield(response, 'results')
   results = response.results;
   fprintf('[%s] %s: %s\n', response.service, results.category, results.msg);
   fprintf('HED version: %s\n', results.hed_version);
   fprintf('Validation errors for %s:\n', dictionary_file)
   fprintf('%s\n', results.data);
end
