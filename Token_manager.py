def _fetch_new_token(self):
        """Fetch a new token from the token URL."""
        st.session_state.token_refresh_count += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 Token Refresh #{st.session_state.token_refresh_count}")
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"🔗 URL: {self.token_url}")
        
        try:
            start_time = datetime.now()
            response = requests.get(self.token_url, timeout=10)
            response_time = (datetime.now() - start_time).total_seconds()
            
            print(f"⏱️ Response time: {response_time:.2f} seconds")
            print(f"📊 Status code: {response.status_code}")
            
            response.raise_for_status()
            token = response.text.strip()
            
            # Enhanced token logging
            print(f"✅ New token details:")
            print(f"  - Full token: {token}")
            print(f"  - Length: {len(token)} characters")
            print(f"  - First 10 chars: {token[:10]}")
            print(f"  - Last 10 chars: {token[-10:]}")
            print(f"{'='*50}\n")
            return token
            
        except requests.Timeout:
            print("⚠️ Token fetch timed out after 10 seconds")
            st.session_state.token_error_count += 1
            raise
        except requests.RequestException as e:
            print(f"❌ Token fetch failed: {str(e)}")
            st.session_state.token_error_count += 1
            raise

    def get_token(self):
        """Get the current token, refreshing if necessary."""
        st.session_state.token_request_count += 1
        current_time = datetime.now()
        
        print(f"\n{'='*50}")
        print(f"🔍 Token Request #{st.session_state.token_request_count}")
        print(f"⏰ Time: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        
        # Token status check with enhanced token logging
        if st.session_state.token and st.session_state.last_refresh:
            time_since_refresh = current_time - st.session_state.last_refresh
            remaining_time = self.cache_duration - time_since_refresh
            
            print(f"📈 Current Token Status:")
            print(f"  - Current token: {st.session_state.token}")
            print(f"  - Token length: {len(st.session_state.token)} characters")
            print(f"  - Age: {time_since_refresh.total_seconds():.2f} seconds")
            print(f"  - Remaining time: {remaining_time.total_seconds():.2f} seconds")
            print(f"  - Total refreshes: {st.session_state.token_refresh_count}")
            print(f"  - Error count: {st.session_state.token_error_count}")
        else:
            print("📝 No active token found")
        
        # Check if token needs refresh
        needs_refresh = (
            st.session_state.token is None or 
            st.session_state.last_refresh is None or
            current_time - st.session_state.last_refresh >= self.cache_duration
        )
        
        if needs_refresh:
            print("\n🔄 Token refresh required")
            print("Previous token: " + (st.session_state.token if st.session_state.token else "None"))
            print(f"Reason: {'Token expired' if st.session_state.token else 'No token exists'}")
            
            try:
                st.session_state.token = self._fetch_new_token()
                st.session_state.last_refresh = current_time
                print("✨ Token refresh successful")
                print(f"New token: {st.session_state.token}")
                
            except Exception as e:
                print(f"❌ Error during refresh: {str(e)}")
                if st.session_state.token is not None:
                    print("⚠️ Using existing token as fallback")
                    print(f"⚠️ Fallback token: {st.session_state.token}")
                    print(f"⚠️ Fallback token age: {(current_time - st.session_state.last_refresh).total_seconds():.2f} seconds")
                    return st.session_state.token
                raise
        else:
            print("\n✅ Using cached token")
            print(f"Current token: {st.session_state.token}")
            print(f"💡 Token is still valid for {(self.cache_duration - (current_time - st.session_state.last_refresh)).total_seconds():.2f} seconds")
            
        print(f"{'='*50}\n")
        return st.session_state.token
