using System;
using System.IO;

namespace png2base64
{
    class Program
    {
        /// <summary>
        /// 
        /// </summary>
        /// <param name="plainText"></param>
        /// <returns></returns>
        public static string Base64Encode(string plainText)
        {
            // thanks stackoverflow: https://stackoverflow.com/questions/11743160/how-do-i-encode-and-decode-a-base64-string
            var plainTextBytes = System.Text.Encoding.UTF8.GetBytes(plainText);
            return System.Convert.ToBase64String(plainTextBytes);
        }

        static void ProcessFile(string f)
        {
            Console.WriteLine("Processing file: {0} ...", f);

            string ConstraintText = File.ReadAllText(f);

            File.WriteAllText(f + ".Base64", Base64Encode(ConstraintText));
        }

        static void Main(string[] args)
        {
            string param = args[0];

            if (param != "")
            {
                ProcessFile(param);
            }
        }
    }
}
