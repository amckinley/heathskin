using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Web;
using System.Web.Script.Serialization;
using System.Net;
using System.Diagnostics;
using Microsoft.VisualBasic;
 

namespace wpf_test
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private JavaScriptSerializer Serializer;
        private string AuthToken;
        private CookieContainer Cookies;
        private readonly BackgroundWorker worker;
        private Random random;
        private string hs_log_path;
        private HttpWebRequest upload_request;
        private string LogServerAddress;

        public MainWindow()
        {
            InitializeComponent();
            this.Serializer = new JavaScriptSerializer();
            this.Cookies = new CookieContainer();
            this.random = new Random();
            //this.hs_log_path = "C:\\Program Files (x86)\\Hearthstone\\Hearthstone_Data\\output_log.txt";
            this.hs_log_path = "E:\\blizzard\\Hearthstone\\Hearthstone_Data\\output_log.txt";
            
            // initialize the uploader
            this.worker = new BackgroundWorker();
            this.worker.DoWork += worker_DoWork;
            this.worker.RunWorkerCompleted += worker_RunWorkerCompleted;

            this.LogServerAddress = "10.1.10.20";
        }

        private void worker_DoWork(object sender, DoWorkEventArgs e)
        {
            Directory.SetCurrentDirectory("E:\\");
            using (StreamReader reader = new StreamReader(new FileStream(this.hs_log_path,
                     FileMode.Open, FileAccess.Read, FileShare.ReadWrite)))
            {
                //start at the end of the file
                long lastMaxOffset = reader.BaseStream.Length;

                while (true)
                {
                    //if the file size has not changed, idle
                    if (reader.BaseStream.Length == lastMaxOffset)
                        continue;

                    //seek to the last max offset
                    reader.BaseStream.Seek(lastMaxOffset, SeekOrigin.Begin);

                    //read out of the file until the EOF
                    string line = "";
                    List<string> lines = new List<string>();
                    while ((line = reader.ReadLine()) != null)
                    {
                        lines.Add(line);
                    }

                    this.Dispatcher.Invoke((Action)(() =>
                    {
                        this.UploadLines(lines);
                    }));
                    //update the last max offset
                    lastMaxOffset = reader.BaseStream.Position;
                }
            }
        }

        private void worker_RunWorkerCompleted(object sender,
                                               RunWorkerCompletedEventArgs e)
        {
            //update ui once worker complete his work
        }

        private void DoLogin(string Username, string Password)
        {
            UploaderStatusBox.Text = "Starting login...";
            string login_json = this.Serializer.Serialize(new
            {
                email = Username,
                password = Password
            });
            var request = (HttpWebRequest)WebRequest.Create("http://" + this.LogServerAddress + ":3000/login");
            request.CookieContainer = this.Cookies;
            request.ContentType = "application/json";
            request.Method = "POST";

            WriteCredential("foo", "bar", "baz");

            using (var streamWriter = new StreamWriter(request.GetRequestStream()))
            {
                streamWriter.Write(login_json);
                streamWriter.Flush();
                streamWriter.Close();

                var httpResponse = (HttpWebResponse)request.GetResponse();
                UploaderStatusBox.Text = "Fetching auth token...";
                using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
                {
                    var result = streamReader.ReadToEnd();
                    this.AuthToken = ExtractAuthToken(result);
                }
            }

            this.StartSession();
        }

        private void StartSession()
        {
            UploaderStatusBox.Text = "Starting logging session...";
            var request = (HttpWebRequest)WebRequest.Create("http://" + this.LogServerAddress + ":3000/start_session");
            request.CookieContainer = this.Cookies;
            request.Headers.Set("Authentication-Token", this.AuthToken);
            request.Method = "POST";

            var httpResponse = (HttpWebResponse)request.GetResponse();
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                var result = streamReader.ReadToEnd();

                LogSnippet.Text = result;
            }
            UploaderStatusBox.Text = "Session started; ready to log";

        }

        private HttpWebRequest CreateUploadRequest()
        {
            var upload_request = (HttpWebRequest)WebRequest.Create("http://" + this.LogServerAddress +  ":3000/upload_lines");
            upload_request.CookieContainer = this.Cookies;
            upload_request.Headers.Set("Authentication-Token", this.AuthToken);
            upload_request.ContentType = "application/json";
            upload_request.Method = "POST";
            upload_request.Proxy = null;
            return upload_request;
        }

        private void UploadLine(string line)
        {
            string logline_json = this.Serializer.Serialize(new
            {
                log_line = line
            });
            var request = this.CreateUploadRequest();

            using (var streamWriter = new StreamWriter(request.GetRequestStream()))
            {
                streamWriter.Write(logline_json);
                streamWriter.Flush();
                streamWriter.Close();

                var httpResponse = (HttpWebResponse)request.GetResponse();
                httpResponse.Close();
            }
        }

        private void UploadLines(List<string> lines)
        {
            string logline_json = this.Serializer.Serialize(new
            {
                log_lines = lines
            });
            var request = this.CreateUploadRequest();

            using (var streamWriter = new StreamWriter(request.GetRequestStream()))
            {
                streamWriter.Write(logline_json);
                streamWriter.Flush();
                streamWriter.Close();

                var httpResponse = (HttpWebResponse)request.GetResponse();
                httpResponse.Close();
            }
        } 

        private string ExtractAuthToken(string json_blob)
        {
            Dictionary<string, object> dict = this.Serializer.Deserialize<Dictionary<string, object>>(json_blob);
            Dictionary<string, object> response_dict = (Dictionary<string, object>)dict["response"];
            Dictionary<string, object> user = (Dictionary<string, object>)response_dict["user"];
            var auth_token = user["authentication_token"];
            return auth_token.ToString();
        }

        private void StopLogger()
        {
            this.Serializer = new JavaScriptSerializer();
            this.Cookies = new CookieContainer();
            this.AuthToken = null;
        }

        private void ConnectLogger_Click(object sender, RoutedEventArgs e)
        {
            // no more edits
            Username.IsEnabled = false;
            Password.IsEnabled = false;
            ConnectLogger.IsEnabled = false;
            LogFilePath.IsEnabled = false;

            // login and get the auth token
            this.DoLogin(Username.Text, Password.Password);

            // setup the session for the upload requests
            this.CreateUploadRequest();

            // start the tailer
            this.worker.RunWorkerAsync();

            //while (true)
            //{
            //    this.UploadLine("foobar");
            //}

            // if success, show the disconnect button
            DisconnectLogger.Visibility = Visibility.Visible;
        }

        private void DisconnectLogger_Click(object sender, RoutedEventArgs e)
        {
            // everything editable again
            Username.IsEnabled = true;
            Password.IsEnabled = true;
            ConnectLogger.IsEnabled = true;
            LogFilePath.IsEnabled = true;

            // turn the button back off
            DisconnectLogger.Visibility = Visibility.Hidden;

            // clear the logger
            LogSnippet.Text = "";
        }
    }
}
